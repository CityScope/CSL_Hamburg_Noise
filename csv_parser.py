import csv
import json


# read the road info from the csv
def get_road_info_for_road_id(road_id):
    with open('roads.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row_id, row in enumerate(csv_reader):
            if row_id == 0:
                # ignore header
                continue
            if road_id == int(row[0]):
                return {
                    'max_speed': row[1],
                    'light_vehicle_count':  row[2],
                    'heavy_vehicle_count':  row[3],
                    'average_speed':  row[4],
                }

