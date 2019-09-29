from shapely.geometry import Polygon, polygon
import json

def analyze_result(geojson_path):
    geojson = get_result_json(geojson_path)
    features = geojson['features']
    result_areas = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]

    for feature in features:
        print(feature['geometry']['coordinates'][0])
        feature_polygon = Polygon(feature['geometry']['coordinates'][0])
        result_areas[feature['properties']['idiso']] += feature_polygon.intersection(get_grasbrook_polygon()).area

    for key, result_area in enumerate(result_areas):
        print('idiso:', key, ' area:', round(result_area))


def get_grasbrook_polygon():
    with open('../grasbrook_land.geojson') as g:
        grasbrook = json.load(g)

    return Polygon(grasbrook['features'][2]['geometry']['coordinates'][0])

def get_result_json(result_json_path):
    with open(result_json_path) as f:
        return json.load(f)



if __name__ == "__main__":

    analyze_result('./results/result2.geojson')
