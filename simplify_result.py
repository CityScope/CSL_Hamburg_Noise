import os
import json
import visvalingamwyatt as vw
import configparser
from shapely.geometry import shape, Point

config = configparser.ConfigParser()
config.read('config.ini')

cwd = os.path.dirname(os.path.abspath(__file__))
buildings_path = os.path.abspath(cwd + "/input_geojson/design/buildings/buildings.json/")


# load a json from a path
def load_json_from_path(json_path):
    with open(json_path) as f:
        return json.load(f)


# the noise result is subdivided in to 4 cells, listed by cell_id. Check which cells contain buildings
def get_cell_ids_containing_buildings(result, buildings):
    noise_result_cells_containing_buildings = []

    # check each polygon to see if it contains the point
    for feature in result['features']:
        polygon = shape(feature['geometry'])
        for building in buildings['features']:
            print(building)
            for corner in building['geometry']['coordinates'][0]:
                point = Point(corner)
                if polygon.contains(point):
                    print 'Found containing polygon:', feature
                    noise_result_cells_containing_buildings.append(feature['properties']['cell_id'])

    return noise_result_cells_containing_buildings


# takes the path to a result geojson and simplifies the geometry in order to reduce file size
def simplify_result(result_path):
    result_geojson = load_json_from_path(result_path)
    buildings_geojson = load_json_from_path(config['SETTINGS']['INPUT_JSON_BUILDINGS'])
    areas_containing_buildings = get_cell_ids_containing_buildings(result_geojson, buildings_geojson)
    simplified_features = []

    # simplify all features
    # cell_id here refers to 1 of 4 cells that the noise software creates to split the calculated area into a grid
    # they are not related to city_scope cells
    for feature in result_geojson['features']:
        # heavily simplify feature geometry if not in a cell containing buildings.
        if feature['properties']['cell_id'] not in areas_containing_buildings:
            feature['geometry'] = vw.simplify_geometry(feature['geometry'], ratio=0.3)
            simplified_features.append(feature)
        # simplify only lightly if cell_id contains buildings
        else:
            feature['geometry'] = vw.simplify_geometry(feature['geometry'], ratio=0.8)
            simplified_features.append(feature)

    result_geojson['features'] = simplified_features

    return result_geojson
