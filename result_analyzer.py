from shapely.geometry import Polygon, polygon
import json

def analyze_result(geojson, grasbrook):
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
        result_areas[feature['properties']['idiso']] += feature_polygon.intersection(grasbrook).area

    for key, result_area in enumerate(result_areas):
        print('idiso:', key, ' area:', round(result_area))


if __name__ == "__main__":

    with open('./results/result.geojson') as f:
        geojson = json.load(f)
    with open('../grasbrook_land.geojson') as g:
        grasbrook = json.load(g)


    print(grasbrook)
    grasbrook_polygon = Polygon(grasbrook['features'][2]['geometry']['coordinates'][0])


    analyze_result(geojson, grasbrook_polygon)