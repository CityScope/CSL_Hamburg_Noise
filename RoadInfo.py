#!/usr/bin/env python2.7

# TODO make getter for road type specific traffic data etc
class RoadInfo:
    # defining constructor
    def __init__(self, road_id, geom, road_type, start_point, end_point, max_speed, car_traffic, truck_traffic,
                 train_speed, train_per_hour, ground_type, has_anti_vibration):
        self.road_id = road_id
        self.geom = geom
        self.road_type = road_type
        self.start_point = start_point
        self.end_point = end_point
        self.max_speed = max_speed
        self.car_traffic = car_traffic
        self.truck_traffic = truck_traffic
        self.train_speed = train_speed
        self.train_per_hour = train_per_hour
        self.ground_type_train_track = ground_type
        self.has_anti_vibration = has_anti_vibration

        # defining class methods

    def get_road_id(self):
        return (self.road_id)

    def get_road_type(self):
        return (self.road_type)

    def get_road_type_for_query(self):
        return (self.road_type)

    def get_start_point(self):
        return (self.start_point)

    def get_end_point(self):
        return (self.end_point)

    def get_geom(self):
        return (self.geom)

    def get_max_speed(self):
        return (self.max_speed)

    def get_car_traffic(self):
        return self.car_traffic

    def get_truck_traffic(self):
        return self.truck_traffic

    def get_train_speed(self):
        return self.train_speed

    def get_train_per_hour(self):
        return self.train_per_hour

    def get_ground_type_train_track(self):
        return self.ground_type_train_track

    def is_anti_vibration(self):
        return self.has_anti_vibration
