#!/usr/bin/env python2.7

# a class describing a city scope table

from shapely.geometry import Point
import json
import urllib
import pyproj


class CityScopeTable:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, address):
        self.address = address

        self.result = json.load(urllib.urlopen(self.address))
        self.start_cell_origin = (Point(self.result['header']['spatial']['latitude'], self.result['header']['spatial']['longitude']))
        self.table_rotation = self.result['header']['spatial']['rotation']  # TODO can the table rotation be different form the cell rotation??
        self.table_cell_size = self.result['header']['spatial']['cellSize']
        self.table_row_count = self.result['header']['spatial']['nrows']
        self.table_column_count = self.result['header']['spatial']['ncols']

    def get_result(self):
        return self.result

    def get_start_cell_origin_epsg(self):
        return self.reproject_origin()

    def get_start_cell_origin_wgs(self):
        return self.start_cell_origin

    def get_table_rotation(self):
        return self.table_rotation

    def get_table_cell_size(self):
        return self.table_cell_size

    def get_table_row_count(self):
        return self.table_row_count

    def get_table_column_count(self):
        return self.table_column_count

    def reproject_origin(self):
        wgs84 = pyproj.Proj("+init=EPSG:4326")
        espg = pyproj.Proj("+init=EPSG:25832")
        origin_x, origin_y = pyproj.transform(wgs84, espg, self.start_cell_origin.y, self.start_cell_origin.x)

        return Point(origin_y, origin_x)