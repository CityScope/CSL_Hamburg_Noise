#!/usr/bin/env python2.7

import json
import os
import numpy
from geomet import wkt
import RoadInfo
from config_loader import get_config

cwd = os.path.dirname(os.path.abspath(__file__))

# TODO: all coordinates for roads and buildings are currently set to z level 0

# settings for the static input data
config = get_config()

include_rail_road = config['NOISE_SETTINGS'].getboolean('INCLUDE_RAILROAD')
include_lower_main_road = config['NOISE_SETTINGS'].getboolean('INCLUDE_LOWER_MAIN_ROAD')
upper_main_road_as_multi_line = config['NOISE_SETTINGS'].getboolean('UPPER_MAIN_ROAD_AS_MULTI_LINE')

# dynamic input data from designer
buildings_json = config['NOISE_SETTINGS']['INPUT_JSON_BUILDINGS']

# static input data
road_network_json = config['NOISE_SETTINGS']['INPUT_JSON_ROAD_NETWORK']
railroad_multi_line_json = os.path.abspath(cwd + '/input_geojson/static/roads/railroads.json')

# road names from julias shapefile : road_type_ids from IffStar NoiseModdeling
noise_road_types = {
    "hauptverkehrsstrasse": 56,  # in boulevard 70km/h
    "hauptsammelstrasse": 53,  # extra boulevard Street 50km/h
    "anliegerstrasse": 54,  # extra boulevard Street <50km/,
    "eisenbahn": 99  # railroad
}

all_roads = []


# opens a json from path
def open_geojson(path):
    with open(path) as f:
        return json.load(f)


# extract traffic data from road properties
def get_car_traffic_data(road_properties):
    #  https://d-nb.info/97917323X/34
    # p. 68, assuming a mix of type a) and type b) for car traffic around grasbrook (strong morning peak)
    # most roads in hamburg belong to type a) or b)
    # assuming percentage of daily traffic in peak hour = 11%
    # truck traffic: the percentage of daily traffic in peak hour seems to be around 8%
    # source. https://bast.opus.hbz-nrw.de/opus45-bast/frontdoor/deliver/index/docId/1921/file/SVZHeft29.pdf

    # Sources daily traffic: HafenCity GmbH , Standortanalyse, S. 120

    if road_properties['eisenbahn']:
        return None, None, None

    car_traffic = int(int(road_properties['car_traffic_daily']) * 0.11)
    truck_traffic = int(int(road_properties['truck_traffic_daily']) * 0.08)
    max_speed = int(road_properties['max_speed'])

    return max_speed, car_traffic, truck_traffic

# source for train track data = http://laermkartierung1.eisenbahn-bundesamt.de/mb3/app.php/application/eba
def get_train_track_data(road_properties):
    if not road_properties['eisenbahn']:
        return None, None, None, None

    train_speed = road_properties['train_speed']
    train_per_hour = road_properties['trains_per_hour']
    ground_type = road_properties['ground_type']
    has_anti_vibration = road_properties['has_anti_vibration']

    return train_speed, train_per_hour, ground_type, has_anti_vibration


def get_road_queries():
    features = get_roads_features()
    add_third_dimension_to_features(features)

    for feature in features:
        id = feature['properties']['id']
        road_type = get_road_type(feature['properties'])
        coordinates = feature['geometry']['coordinates']

        # input road type might not be defined. road is not imported # TODO consider using a fallback
        if road_type == 0:
            continue
        if feature['geometry']['type'] == 'MultiLineString':
            # beginning point of the road
            start_point = coordinates[0][0]
            # end point of the road
            end_point = coordinates[-1][-1]
        else:
            # beginning point of the road
            start_point = coordinates[0]
            # end point of the road
            end_point = coordinates[1]
            # build string containing all coordinates

        geom = wkt.dumps(feature['geometry'], decimals=0)

        max_speed, car_traffic, truck_traffic = get_car_traffic_data(feature['properties'])
        train_speed, train_per_hour, ground_type, has_anti_vibration = get_train_track_data(feature['properties'])

        road_info = RoadInfo.RoadInfo(id, geom, road_type, start_point, end_point, max_speed, car_traffic,
                                      truck_traffic,
                                      train_speed, train_per_hour, ground_type, has_anti_vibration)
        all_roads.append(road_info)

    nodes = create_nodes(all_roads)
    sql_insert_strings = []
    for road in all_roads:
        sql_insert_string = get_insert_query_for_road(road, nodes)
        sql_insert_strings.append(sql_insert_string)

    return sql_insert_strings


# returns sql queries for the traffic table,
def get_traffic_queries():
    sql_insert_strings_noisy_roads = []
    nodes = create_nodes(all_roads)
    for road in all_roads:
        node_from = get_node_for_point(road.get_start_point(), nodes)
        node_to = get_node_for_point(road.get_end_point(), nodes)

        if road.get_road_type_for_query() == noise_road_types['eisenbahn']:
            # train traffic
            train_speed = road.get_train_speed()
            trains_per_hour = road.get_train_per_hour()
            ground_type = road.get_ground_type_train_track()
            has_anti_vibration = road.is_anti_vibration()

            sql_insert_string = "INSERT INTO roads_traffic (node_from,node_to, train_speed, trains_per_hour, ground_type, has_anti_vibration) " \
                                "VALUES ({0},{1},{2},{3},{4},{5});".format(
                node_from, node_to, train_speed, trains_per_hour, ground_type, has_anti_vibration)
        else:
            # car traffic
            traffic_cars = road.get_car_traffic()
            traffic_trucks = road.get_truck_traffic()
            max_speed = road.get_max_speed()
            load_speed = max_speed * 0.9
            junction_speed = max_speed * 0.85

            sql_insert_string = "INSERT INTO roads_traffic (node_from,node_to,load_speed,junction_speed,max_speed,lightVehicleCount,heavyVehicleCount) " \
                                "VALUES ({0},{1},{2},{3},{4},{5},{6});".format(node_from, node_to, load_speed,
                                                                               junction_speed, max_speed, traffic_cars,
                                                                               traffic_trucks)
        sql_insert_strings_noisy_roads.append(sql_insert_string)

    return sql_insert_strings_noisy_roads


# get sql queries for the buildings
def get_building_queries():
    # A multipolygon containing all buildings
    data = open_geojson(cwd + "/" + config['NOISE_SETTINGS']['INPUT_JSON_BUILDINGS'])
    sql_insert_strings_all_buildings = []

    for feature in data['features']:
        if not "coordinates" in feature['geometry']:
            continue
        for polygon in feature['geometry']['coordinates']:
            polygon_string = ''
            for coordinates_list in polygon:
                line_string_coordinates = ''
                try:
                    for coordinate_pair in coordinates_list:
                        # append 0 to all coordinates for mock third dimension
                        coordinate_string = str(coordinate_pair[0]) + ' ' + str(coordinate_pair[1]) + ' ' + str(0) + ','
                        line_string_coordinates += coordinate_string
                        # remove trailing comma of last coordinate
                    line_string_coordinates = line_string_coordinates[:-1]
                except Exception as e:
                    print("invalid json")
                    print(e)
                    print(feature)
                    exit()
                # create a string containing a list of coordinates lists per linestring
                #   ('PolygonWithHole', 'POLYGON((0 0, 10 0, 10 10, 0 10, 0 0),(1 1, 1 2, 2 2, 2 1, 1 1))'),
                polygon_string += '(' + line_string_coordinates + '),'
            # remove trailing comma of last line string
            polygon_string = polygon_string[:-1]
            sql_insert_string = "'POLYGON (" + polygon_string + ")'"
            sql_insert_strings_all_buildings.append(sql_insert_string)

    return sql_insert_strings_all_buildings


# merges the design input for roads and the static road features
# returns a list of geojson features containing all relevant roads
def get_roads_features():
    road_network = open_geojson(cwd + "/" + road_network_json)['features']

    if include_rail_road:
        for feature in open_geojson(railroad_multi_line_json)['features']:
            road_network.append(feature)

    return road_network


# create nodes for all roads - nodes are connection points of roads
def create_nodes(all_roads):
    nodes = []
    for road in all_roads:
        coordinates_start_point = road.get_start_point()
        nodes.append(coordinates_start_point)
        coordinates_end_point = road.get_end_point()
        nodes.append(coordinates_end_point)
    unique_nodes = []

    # filter for duplicates
    for node in nodes:
        if not any(numpy.array_equal(node, unique_node) for unique_node in unique_nodes):
            unique_nodes.append(node)
    return unique_nodes


def get_node_for_point(point, nodes):
    dict_of_nodes = {i: nodes[i] for i in range(0, len(nodes))}
    for node_id, node in dict_of_nodes.iteritems():
        if point == node:
            return node_id
    print('could not find node for point', point)
    exit()


def get_road_type(road_properties):
    # if not in road types continue
    for output_road_type in noise_road_types.keys():
        if road_properties['name'] == output_road_type:
            return noise_road_types[output_road_type]

    print('no matching noise road_type_found for', road_properties['name'])
    return 0


def get_insert_query_for_road(road, nodes):
    node_from = get_node_for_point(road.get_start_point(), nodes)
    node_to = get_node_for_point(road.get_end_point(), nodes)

    sql_insert_string = "INSERT INTO roads_geom (the_geom,NUM,node_from,node_to,road_type) " \
                        "VALUES (ST_GeomFromText('{0}'),{1},{2},{3},{4});".format(road.get_geom(), road.get_road_id(),
                                                                                  node_from, node_to,
                                                                                  road.get_road_type_for_query())
    return sql_insert_string


def add_third_dimension_to_features(features):
    for feature in features:
        if feature['geometry']['type'] == 'LineString':
            add_third_dimension_to_line_feature(feature)
        if feature['geometry']['type'] == 'MultiLineString':
            add_third_dimension_to_multi_line_feature(feature)
        # TODO use this for buildings as well


def add_third_dimension_to_multi_line_feature(feature):
    for pointList in feature['geometry']['coordinates']:
        for point in pointList:
            point.append(0)


def add_third_dimension_to_line_feature(feature):
    for point in feature['geometry']['coordinates']:
        point.append(0)
