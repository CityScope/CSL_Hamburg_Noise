#!/usr/bin/env python2.7

# a class describing a city scope table

from shapely.geometry import Point
import json
import urllib
import math
from reproject import reproject_point_to_hamburg_epsg


class CityScopeTable:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, address, table_flipped):
        self.address = address
        self.table_flipped = table_flipped

        self.result = json.load(urllib.urlopen(self.address))
        # Temporary fix, as longitude and latitude are falsely swapped at the endpoint
        #self.start_cell_origin = (Point(self.result['header']['spatial']['longitude'], self.result['header']['spatial']['latitude']))
        self.start_cell_origin = (Point(self.result['header']['spatial']['latitude'], self.result['header']['spatial']['longitude']))
        self.table_rotation = self.result['header']['spatial']['rotation']  # TODO can the table rotation be different form the cell rotation??
        self.table_cell_size = self.result['header']['spatial']['cellSize']
        self.table_row_count = self.result['header']['spatial']['nrows']
        self.table_column_count = self.result['header']['spatial']['ncols']
        self.table_mapping = self.result['header']['mapping']['type']
        # todo enter mapping to get street id

    def get_result(self):
        return self.result

    def get_start_cell_origin_epsg(self):
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
        origin_x, origin_y = reproject_point_to_hamburg_epsg([self.start_cell_origin.x, self.start_cell_origin.y])

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