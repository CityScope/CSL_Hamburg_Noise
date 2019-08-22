#!/usr/bin/env python2.7

import urllib
import configparser
import os
import json
import time
import requests
from noisemap import get_noise_result_address
from parse_city_scope_table import save_buildings_from_city_scope


# check if grid data changed
def check_for_grid_changes(table_url, last_id):
    try:
        hash_id = json.load(urllib.urlopen(table_url + '/meta/hashes/grid'))
    except:
        print('Cant access cityIO')
        hash_id = 0

    grid_changed = (hash_id != last_id)

    return grid_changed, hash_id


if __name__ == "__main__":
    cwd = os.path.dirname(os.path.abspath(__file__))

    # settings for the static input data
    config = configparser.ConfigParser()
    config.read(cwd+'/config.ini')

    result_post_url = config['CITY_SCOPE']['TABLE_URL_RESULT_POST']

    last_table_id = 0
    while True:
        grid_has_changed, last_table_id = check_for_grid_changes(config['CITY_SCOPE']['TABLE_URL_INPUT'], last_table_id)
        if grid_has_changed:
            # get the data from cityIO, convert it to geojson and write it to config['SETTINGS']['INPUT_JSON_BUILDINGS']
            save_buildings_from_city_scope()
            noise_result_address = get_noise_result_address()

            # Also post result to cityIO
            print("trying to post to cityIO")
            post_address = config['CITY_SCOPE']['TABLE_URL_RESULT_POST']
            r = requests.post(post_address, json=noise_result_address)

            if not r.status_code == 200:
                print("could not post result to cityIO")
                print("Error code", r.status_code)
            else:
                print("Successfully posted to cityIO", r.status_code)
        else:
            print("No changes in grid")
            time.sleep(1)


# todo
# token_file = f = open("access_token.txt", "r")
# token = f.read()
#
# url = https: // cityio.media.mit.edu / api / table / hidden_table