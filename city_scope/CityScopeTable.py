#!/usr/bin/env python2.7

# a class describing a city scope table

from shapely.geometry import Point
import json
import urllib
import math
import os
import configparser
import pyproj


# reprojects a point
def reproject_point(current_epsg, new_epsg, point):
    current = pyproj.Proj("+init=epsg:" + current_epsg)
    new = pyproj.Proj("+init=epsg:" + new_epsg)
    projected_x, projected_y = pyproj.transform(current, new, point[0], point[1])

    return projected_x, projected_y


class CityScopeTable:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, address, table_flipped):
        self.address = address
        self.table_flipped = table_flipped

        try:
            self.result = json.load(urllib.urlopen(self.address))
            self.start_cell_origin = (Point(self.result['header']['spatial']['longitude'], self.result['header']['spatial']['latitude']))
        # use local debugging table as fallback
        except:
            print("cannot read from CityIO server. Using local fallback json")
            cwd = os.path.dirname(os.path.abspath(__file__))
            debug_json_path = os.path.abspath(cwd + "/__debugging_virtual_table.json")
            self.result = json.load(open(debug_json_path))
            self.start_cell_origin = (Point(self.result['header']['spatial']['longitude'], self.result['header']['spatial']['latitude']))

        self.table_rotation = self.result['header']['spatial']['rotation']  # TODO can the table rotation be different form the cell rotation??
        self.table_cell_size = self.result['header']['spatial']['cellSize']
        self.table_row_count = self.result['header']['spatial']['nrows']
        self.table_column_count = self.result['header']['spatial']['ncols']
        self.table_mapping = self.result['header']['mapping']['type']
        self.table_cell_content = self.result['header']['block']
        # todo enter mapping to get street id

        # get projections from config.ini
        config = configparser.ConfigParser()
        file_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        config.read(file_path + '/config.ini')
        self.origin_epsg = config['CITY_SCOPE']['GLOBAL_EPSG']
        self.local_epsg = config['CITY_SCOPE']['LOCAL_EPSG']


    def get_result(self):
        return self.result

    def get_projected_start_cell_origin(self):
        origin = self.get_reprojected_origin()
        if not self.table_flipped:
            return origin

        # else: shift the table origin from the SouthEast corner to the NorthWest corner
        return self.get_flipped_origin(origin)

    def get_table_rotation(self):
        return 360 - self.table_rotation

    def get_table_cell_size(self):
        return self.table_cell_size

    def get_table_row_count(self):
        return self.table_row_count

    def get_table_column_count(self):
        return self.table_column_count

    def get_table_mapping(self):
        mapping = self.table_mapping
        mapping.append('unknown')

        return self.table_mapping

    def get_reprojected_origin(self):
        point = [self.start_cell_origin.x, self.start_cell_origin.y]
        origin_x, origin_y = reproject_point(self.origin_epsg, self.local_epsg, point)

        return Point(origin_x, origin_y)

    # returns the opposite corner of the grid (SE->NW)
    def get_flipped_origin(self, origin):
        table_width = self.get_table_column_count() * self.table_cell_size
        table_height = self.get_table_row_count() * self.table_cell_size
        diagonal = math.sqrt(pow(table_width, 2) + pow(table_height, 2))
        diagonal_angle = math.degrees(math.atan(table_width/table_height))
        angle_diagonal_to_x_axis = diagonal_angle - self.get_table_rotation()
        delta_x = math.sin(math.radians(angle_diagonal_to_x_axis)) * diagonal
        delta_y = math.cos(math.radians(angle_diagonal_to_x_axis)) * diagonal
        flipped_x = origin.x - delta_x
        flipped_y = origin.y + delta_y

        return Point(flipped_x, flipped_y)
