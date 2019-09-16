#!/usr/bin/env python2.7

# TODO make getter for road type specific traffic data etc
class RoadInfo:
    # defining constructor
    def __init__(self, road_id, road_type, start_point, end_point, geom):
        self.road_id = road_id
        self.road_type = road_type
        self.start_point = start_point
        self.end_point = end_point
        self.geom = geom

        # defining class methods

    def get_road_id(self):
        return (self.road_id)

    def get_road_type(self):
        return (self.road_type)

    def get_road_type_for_query(self):
        # dirty hack to treat railroads as heavy car roads when making insert queries
        if self.road_type == 99:
            return 56
        return (self.road_type)

    def get_start_point(self):
        return (self.start_point)

    def get_end_point(self):
        return (self.end_point)

    def get_geom(self):
        return (self.geom)

    def is_noisy(self):
        return True

        #if self.get_road_type_for_query() == 56:
         #   return True

#        return False
