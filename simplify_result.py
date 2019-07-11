import os
import json
import visvalingamwyatt as vw
from shapely.geometry import shape, Point
from noisemap import load_json
from draw_map import draw_geojson

cwd = os.path.dirname(os.path.abspath(__file__))
result_geojson_path = os.path.abspath(cwd + "/results/" + "result_new.geojson")
simple_geojson_path = os.path.abspath(cwd + "/results/" + "simple_result.geojson")
buildings_path = os.path.abspath(cwd + "/input_geojson/design/buildings/buildings.json/")

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


result_geojson = load_json(result_geojson_path)
buildings_geojson = load_json(buildings_path)
areas_containing_buildings = get_cell_ids_containing_buildings(result_geojson, buildings_geojson)
simplified_features = []

# TODO simplify only results that are in not in the quadrants containing buildings.
# see simplified_result.png

for feature in result_geojson['features']:
    print(feature)
    if feature['properties']['cell_id'] not in areas_containing_buildings:
        # simplify feature geometry
        print("original", len(feature['geometry']['coordinates'][0]))
        feature['geometry'] = vw.simplify_geometry(feature['geometry'], ratio=0.3)
        print("simple", len(feature['geometry']['coordinates'][0]))
        simplified_features.append(feature)
    else:
        print("not simplified, containing buildings")
        print(feature['properties']['cell_id'])
        # do not simplify
        feature['geometry'] = vw.simplify_geometry(feature['geometry'], ratio=0.8)
        simplified_features.append(feature)


result_geojson['features'] = simplified_features

# overwrite result json with reprojected result
with open(simple_geojson_path, 'wb') as f:
    json.dump(result_geojson, f, sort_keys=True, indent=4, separators=(',', ': '))


draw_geojson(simple_geojson_path)