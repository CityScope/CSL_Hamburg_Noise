import visvalingamwyatt as vw
import os
from noisemap import load_json
import json

cwd = os.path.dirname(os.path.abspath(__file__))
geojson_path = os.path.abspath(cwd + "/results/" + "result.geojson")
simple_geojson_path = os.path.abspath(cwd + "/results/" + "simple_result.geojson")

geojson = load_json(geojson_path)

print(geojson)

# TODO simplify result
simple_geom = vw.simplify_geometry(geojson['features'][0]['geometry'], ratio=0.15)

print(simple_geom)
print(len(geojson['features'][0]['geometry']['coordinates'][0]))
print(len(simple_geom['coordinates'][0]))

geojson['features'][0]['geometry'] = simple_geom

# overwrite result json with reprojected result
with open(simple_geojson_path, 'wb') as f:
    json.dump(geojson, f)
