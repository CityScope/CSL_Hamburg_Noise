#!/usr/bin/env python2.7

import json
import os
import numpy
from geomet import wkt
import RoadInfo
import configparser

cwd = os.path.dirname(os.path.abspath(__file__))

# TODO: all coordinates for roads and buildings are currently set to z level 0

# settings for the static input data
config = configparser.ConfigParser()
config.read('config.ini')

include_rail_road = config['SETTINGS'].getboolean('INCLUDE_RAILROAD')
include_lower_main_road = config['SETTINGS'].getboolean('INCLUDE_LOWER_MAIN_ROAD')
upper_main_road_as_multi_line = config['SETTINGS'].getboolean('UPPER_MAIN_ROAD_AS_MULTI_LINE')

# dynamic input data from designer
road_network_json = config['SETTINGS']['INPUT_JSON_ROAD_NETWORK']
buildings_json = config['SETTINGS']['INPUT_JSON_BUILDINGS']

# static input data
upper_main_road_single_line_json = os.path.abspath(cwd+'/input_geojson/static/roads/upper_main_road_single.json')
upper_main_road_multi_line_json = os.path.abspath(cwd+'/input_geojson/static/roads/upper_main_road_multi.json')
main_road_lower_multi_line_json = os.path.abspath(cwd+'/input_geojson/static/roads/lower_main_road_multi.json')
railroad_multi_line_json = os.path.abspath(cwd+'/input_geojson/static/roads/railroad.json')

# road names from julias shapefile : road_type_ids from IffStar NoiseModdeling
noise_road_types = {
    "hauptverkehrsstrasse": 56,  # in boulevard 70km/h
    "hauptsammelstrasse": 53,  # extra boulevard Street 50km/h
    "anliegerstrasse": 54,  # extra boulevard Street <50km/,
    "eisenbahn": 99  # railroad # TODO gets treated as 56 in sql queries due to missing info on how to handle railroads
}

all_roads = []

# return a list of sql insert-queries to insert all roads into sql table
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
        road_info = RoadInfo.RoadInfo(id, road_type, start_point, end_point, geom)
        all_roads.append(road_info)

    nodes = create_nodes(all_roads)
    sqlInsertStrings = []
    for road in all_roads:
        sqlInsertString = get_insert_query_for_road(road, nodes)
        sqlInsertStrings.append(sqlInsertString)

    return sqlInsertStrings

# returns sql queries for the traffic table,
# TODO for now creates traffic only for roads of type 56
# TODO traffic counts are still subjective numbers
def get_traffic_queries():
    sqlInsertStringsNoisyRoads = []
    nodes = create_nodes(all_roads)
    for road in all_roads:
        if road.is_noisy():
            node_from = get_node_for_point(road.get_start_point(), nodes)
            node_to = get_node_for_point(road.get_end_point(), nodes)

            sqlInsertString = "INSERT INTO roads_traffic (node_from,node_to,load_speed,junction_speed,max_speed,lightVehicleCount,heavyVehicleCount) " \
                              "VALUES ({0},{1},43,42,65,200,650);".format(node_from, node_to)
            sqlInsertStringsNoisyRoads.append(sqlInsertString)

    return sqlInsertStringsNoisyRoads

# get sql queries for the buildings
def get_building_queries():
    data = open_geojson(os.path.abspath(cwd+'/input_geojson/design/buildings/buildings_error.json'))

    sqlInsertStringsAllBuildings = []

    for feature in data['features']:
        buildingCoordinates = ''
        try:
            print(feature)
            print(feature['geometry']['coordinates'])
        except:
            print("invalid json")
            print(feature)
            exit()
        for coordinates in feature['geometry']['coordinates']:
            for coordinate in coordinates:
                print('building', coordinate)
                coordinateString = str(coordinate[0]) + ' ' + str(coordinate[1]) + ' ' + str(0) + ','
                buildingCoordinates += coordinateString
        # remove trailing comma of last coordinate
        buildingCoordinates = buildingCoordinates[:-1]
        # build string for SQL query
        sqlInsertString = "'MULTIPOLYGON (((" + buildingCoordinates + ")))'"

        sqlInsertStringsAllBuildings.append(sqlInsertString)

    return sqlInsertStringsAllBuildings

def open_geojson(path):
    with open(path) as f:
        return json.load(f)

# merges the design input for roads and the static road features
# returns a list of geojson features containing all relevant roads
def get_roads_features():
    road_network = open_geojson(road_network_json)['features']
    static_features = []

    # set source for upper main road
    if upper_main_road_as_multi_line:
        static_features.append(open_geojson(upper_main_road_multi_line_json)['features'])
    else:
        static_features.append(open_geojson(upper_main_road_single_line_json)['features'])

    if include_lower_main_road:
        static_features.append(open_geojson(main_road_lower_multi_line_json)['features'])

    if include_rail_road:
        static_features.append(open_geojson(railroad_multi_line_json)['features'])

    for feature_set in static_features:
        for feature in feature_set:
            road_network.append(feature)

    return road_network

# create nodes for all roads - nodes are connection points of roads
# TODO: do not connect railway and roads
# TODO : do not connect ends of multilinestring
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
    dictOfNodes = {i: nodes[i] for i in range(0, len(nodes))}
    for node_id, node in dictOfNodes.iteritems():
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

    sqlInsertString = "INSERT INTO roads_geom (the_geom,NUM,node_from,node_to,road_type) " \
                      "VALUES (ST_GeomFromText('{0}'),{1},{2},{3},{4});".format(road.get_geom(), road.get_road_id(),
                                                                              node_from, node_to, road.get_road_type_for_query())
    return sqlInsertString

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

