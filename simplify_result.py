import visvalingamwyatt as vw
import os
from noisemap import load_json
import json

cwd = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.abspath(cwd + "/results/" + "result.geojson")
simple_geojson_path = os.path.abspath(cwd + "/results/" + "simple_result.geojson")

geojson = load_json(geojson_path)

simplified_features = []

for feature in geojson['features']:
    # simplify feature geometry
    print("original", len(feature['geometry']['coordinates'][0]))
    feature['geometry'] = vw.simplify_geometry(feature['geometry'], ratio=0.15)
    print("simple", len(feature['geometry']['coordinates'][0]))
    simplified_features.append(feature)

geojson['features'] = simplified_features



# overwrite result json with reprojected result
with open(simple_geojson_path, 'wb') as f:
    json.dump(geojson, f, sort_keys=True, indent=4, separators=(',', ': '))
