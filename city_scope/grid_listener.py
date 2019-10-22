#!/usr/bin/env python2.7

import urllib
import configparser
import os
import json
import time
import requests
from noisemap import get_result_file_path
from parse_city_scope_table import save_buildings_from_city_scope
from config_loader import get_config


# check if grid data changed
def check_for_grid_changes(table_url, last_id):
    try:
        hash_id = json.load(urllib.urlopen(table_url + '/meta/hashes/grid'))
    except:
        print('Cant access cityIO')
        hash_id = 0

    grid_changed = (hash_id != last_id)

    return grid_changed, hash_id


# checks for updates on the cityIO grid
# If the grid changes the city-scope parser is called to create a new buildings.json
# The noise calculation is triggered
if __name__ == "__main__":
    config = get_config()

    result_post_url = config['CITY_SCOPE']['TABLE_URL_RESULT_POST']

    last_table_id = 0

    while True:
        grid_has_changed, last_table_id = check_for_grid_changes(config['CITY_SCOPE']['TABLE_URL_INPUT'], last_table_id)
        if grid_has_changed:
            # get the data from cityIO, convert it to geojson and write it to config['SETTINGS']['INPUT_JSON_BUILDINGS']
            save_buildings_from_city_scope()
            # start noise calculation
            noise_result_address = get_result_file_path()

            with open(noise_result_address) as f:
                # Also post result to cityIO
                print("trying to post to cityIO")
                post_address = config['CITY_SCOPE']['TABLE_URL_RESULT_POST']
                r = requests.post(post_address, json=json.load(f))

                if not r.status_code == 200:
                    print("could not post result to cityIO")
                    print("Error code", r.status_code)
                else:
                    print("Successfully posted to cityIO", r.status_code)
        else:
            print("No changes in grid")
            time.sleep(1)


