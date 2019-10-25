import os
import configparser


# returns the config
def get_config():
    noise_directory = os.path.dirname(__file__)
    # settings for the static input data
    config = configparser.ConfigParser()
    config.read(noise_directory + '/config.ini')

    return config
