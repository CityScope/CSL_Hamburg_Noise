import pyproj
import json


def open_geojson(path):
    with open(path) as f:
        return json.load(f)

# gets the path for the reprojected json
def get_projected_json_path(original_json_path):
    if original_json_path.endswith('.geojson'):
        return original_json_path[:-8] + '_wgs84' + '.json'
    raise NameError('Invalid path to original json. Must end on ".geojson"')


def save_reprojected_copy_of_geojson_epsg_to_wgs(path_to_geojson):
    result_json = open_geojson(path_to_geojson)
    features = result_json['features']
    wgs84 = pyproj.Proj("+init=EPSG:4326")
    espg = pyproj.Proj("+init=EPSG:25832")

    for feature in features:
        coordinates = feature['geometry']['coordinates']
        for point in coordinates[0]:
            projected_x, projected_y = pyproj.transform(espg, wgs84, point[0], point[1])
            # replace coordinates with projected ones in lat, long format
            point[0] = projected_x
            point[1] = projected_y

    projected_features = features
    result_json['features'] = projected_features
    print(result_json)

    # save projected json
    path_to_projected_json = get_projected_json_path(path_to_geojson)

    with open(path_to_projected_json, 'wb') as f:
        json.dump(result_json, f)

