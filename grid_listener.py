#!/usr/bin/env python2.7

import urllib
import json
import time
import requests
from noisemap import perform_noise_calculation
from city_scope.parse_city_scope_table import save_buildings_from_city_scope
from config_loader import get_config
import argparse
import cityio_socket

# checks for updates on the cityIO grid
# If the grid changes the city-scope parser is called to create a new buildings.json
# The noise calculation is triggered
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='calculate noise levels from cityIO.')
    parser.add_argument('--endpoint', type=int, default=-1,help="endpoint url to choose from config.ini/input_urls")
    args = parser.parse_args()
    print("endpoint",args.endpoint)

    # auth
    try:
        with open("token.txt") as f:
            token=f.readline()
        if token=="": token = None # happens with empty file
    except IOError:
        token=None

    oldHash = ""

    while True:      
        gridHash = cityio_socket.getCurrentState("meta/hashes/grid", int(args.endpoint), token)  
        if gridHash != {} and gridHash != oldHash:
            # get the data from cityIO, convert it to geojson and write it to config['SETTINGS']['INPUT_JSON_BUILDINGS']
            save_buildings_from_city_scope()
            # start noise calculation
            noise_result_address = perform_noise_calculation()

            with open(noise_result_address) as f:
                resultdata = json.load(f)
                resultdata["grid_hash"] = gridHash # state of grid, the results are based on

                # Also post result to cityIO
                print("trying to post to cityIO")
                cityio_socket.sendToCityIO(resultdata, int(args.endpoint), token)
            oldHash = gridHash
        else:
            print("No changes in grid")
            time.sleep(5)


