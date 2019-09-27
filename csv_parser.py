import csv
import json

# opens a json from path
def get_road_geojson():
    with open('/input_geojson/design/roads/road_network_empty.json') as f:
        return json.load(f)


# read the road info from the csv
def get_road_info_for_road_id(road_id):
    with open('roads.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        geojson = get_road_geojson()

        for row in csv_reader:
            if road_id == row[0]:

                return {
                    'light_vehicle_count':  row[1],
                    'heavy_vehicle_count':  row[2],
                    'average_speed':  row[5],
                    'max_speed':  row[7],
                }