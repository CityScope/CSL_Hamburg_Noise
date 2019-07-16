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
    simplified_features = []

    for feature in result_geojson['features']:
        # do not simplify features with interior rings as that leads to error
        if (len(feature['geometry']['coordinates']) >1):
            simplified_features.append(feature)
            continue
        # only simplify complex geometries, as simple geometries might be buildings
        if len(feature['geometry']['coordinates'][0]) < 20:
            simplified_features.append(feature)
            continue
        # simplify complex polygons
        feature['geometry'] = vw.simplify_geometry(feature['geometry'], threshold=0.85)
        simplified_features.append(feature)

    result_geojson['features'] = simplified_features

    return result_geojson
