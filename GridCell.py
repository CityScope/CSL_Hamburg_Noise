#!/usr/bin/env python2.7

# a class describing a squared cell in a city scope grid
import geopy
import geopy.distance


class GridCell:
    # defining constructor
    # origin is the upper left corner
    def __init__(self, origin, rotation, cell_size, cell_type, height):
        self.origin = origin
        self.rotation = rotation
        self.cell_size = cell_size
        self.cell_type = cell_type
        self.height = height

        # defining class methods
    def get_origin(self):
        return (self.origin)

    def get_rotation(self):
        return (self.rotation)

    def get_cell_size(self):
            return (self.cell_size)

    def get_cell_type(self):
            return (self.cell_type)

    def get_height(self):
            return (self.height)

    def get_upper_right_corner(self):
        return self.get_cell_corner(90)

    def get_lower_right_corner(self):
        return self.get_cell_corner(135)

    def get_lower_left_corner(self):
        return self.get_cell_corner(180)

    # gets the cell corner as a point with coordinates.
    def get_cell_corner(self, angle):
        start = self.get_origin()

        # Define a general distance object, initialized with a distance of cell_size.
        d = geopy.distance.VincentyDistance(meters = self.get_cell_size()) # TODO can you enter meters?

        # `destination` method uses a bearing of in degrees to get a distance in a certain direction (90 for east, ..)
        # the resulting bearing is the angle of the desired cell corner plus the rotation of cell
        bearing = self.get_rotation() + angle
        point = d.destination(point=self.get_origin(), bearing=bearing)

        return point



