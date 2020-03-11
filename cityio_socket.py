import json
import requests
from config_loader import get_config

def getCurrentState(topic="", endpoint=-1, token=None):
    config = get_config()
    if endpoint == -1 or endpoint == None:
        get_address = config['CITY_SCOPE']['TABLE_URL_INPUT']+topic
    else:
        get_address = json.loads(config['CITY_SCOPE']['TABLE_URL_INPUT_LIST'])[endpoint]+topic

    try:
        if token is None or endpoint == -1 or endpoint is None:
            r = requests.get(get_address, headers={'Content-Type': 'application/json'})
        else:
            r = requests.get(get_address, headers={'Content-Type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(token).rstrip()})
        if not r.status_code == 200:
            print("could not get from cityIO", get_address)
            print("Error code", r.status_code)
            return {}

        return r.json()
    
    except requests.exceptions.RequestException as e:
        print("CityIO error while GETting!" + e)
        return {}

def sendToCityIO(data, endpoint=-1, token=None):
    config = get_config()
    if endpoint == -1 or endpoint == None:
        post_address = config['CITY_SCOPE']['TABLE_URL_RESULT_POST'] # default endpoint
    else:
        post_address = json.loads(config['CITY_SCOPE']['TABLE_URL_RESULT_POST_LIST'])[endpoint] # user endpoint

    try:
        if token is None or endpoint == -1:
            r = requests.post(post_address, json=data, headers={'Content-Type': 'application/json'})
        else: # with authentication
            r = requests.post(post_address, json=data,
                            headers={'Content-Type': 'application/json',
                                    'Authorization': 'Bearer {}'.format(token).rstrip()})
        print(r)
        if not r.status_code == 200:
            print("could not post result to cityIO", post_address)
            print("Error code", r.status_code)
        else:
            print("Successfully posted to cityIO", post_address, r.status_code)

    except requests.exceptions.RequestException as e:
        print("CityIO error while POSTing!" + e)
        return