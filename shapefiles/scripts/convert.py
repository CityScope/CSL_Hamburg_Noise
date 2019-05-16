#!/usr/bin/env python2.7

import shapefile
import json
import argparse

def convert(input_file_path, output_file_path):
    reader = shapefile.Reader(input_file_path)

    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr)) 
    
    geojson = open(output_file_path, "w")
    geojson.write(json.dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
    geojson.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert shape to geojson")
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    convert(args.input_file,args.output_file)