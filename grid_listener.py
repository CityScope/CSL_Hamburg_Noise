#!/usr/bin/env python2.7

import urllib
import json
import time
import requests
from noisemap import perform_noise_calculation
from city_scope.parse_city_scope_table import save_buildings_from_city_scope
from config_loader import get_config
import argparse


# check if grid data changed
def check_for_grid_changes(table_url, last_id):
    try:
        hash_id = json.load(urllib.urlopen(table_url + '/meta/hashes/grid'))
    except:
        print('Cant access cityIO at',table_url)
        hash_id = 0 # TODO: shouldn't this be last_id? in case, connection fails during later iterations?

    grid_changed = (hash_id != last_id)

    return grid_changed, hash_id

def sendToCityIO(data, endpoint=-1, token=None):
    config = get_config()
    if endpoint == -1 or endpoint == None:
        post_address = config['CITY_SCOPE']['TABLE_URL_RESULT_POST'] # default endpoint
    else:
        post_address = json.loads(config['CITY_SCOPE']['TABLE_URL_RESULT_POST_LIST'])[endpoint] # user endpoint

    if token is None:
        r = requests.post(post_address, json=data, headers={'Content-Type': 'application/json'})
    else: # with authentication
        r = requests.post(post_address, json=data, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer '+token})
    print(r)
    if not r.status_code == 200:
        print("could not post result to cityIO", post_address)
        print("Error code", r.status_code)
    else:
        print("Successfully posted to cityIO", post_address, r.status_code)

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

    config = get_config()
    result_post_url = config['CITY_SCOPE']['TABLE_URL_RESULT_POST']

    last_table_id = 0

    if args.endpoint == "-1":
        cityIO_url = config['CITY_SCOPE']['TABLE_URL_INPUT']
    else:
        cityIO_url = json.loads(config['CITY_SCOPE']['TABLE_URL_INPUT_LIST'])[int(args.endpoint)]

    while True:        
        grid_has_changed, gridHash = check_for_grid_changes(cityIO_url, last_table_id)
        if grid_has_changed:
            # get the data from cityIO, convert it to geojson and write it to config['SETTINGS']['INPUT_JSON_BUILDINGS']
            save_buildings_from_city_scope(cityIO_url)
            # start noise calculation
            noise_result_address = perform_noise_calculation()

            with open(noise_result_address) as f:
                resultdata = json.load(f)
                resultdata["grid_hash"] = last_table_id # state of grid, the results are based on

                # Also post result to cityIO
                print("trying to post to cityIO")
                # sendToCityIO(resultdata, int(args.endpoint), token)
        else:
            print("No changes in grid")
            time.sleep(5)


