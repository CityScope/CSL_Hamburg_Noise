#!/usr/bin/env python2.7

class RoadInfo:
    # defining constructor
    def __init__(self, road_id, road_type, start_point, end_point, geom, traffic_info):
        self.road_id = road_id
        self.road_type = road_type
        self.start_point = start_point
        self.end_point = end_point
        self.geom = geom
        self.light_vehicle_count_off_peak = traffic_info['light_vehicle_count_off_peak']
        self.heavy_vehicle_count_off_peak = traffic_info['heavy_vehicle_count_off_peak']
        self.light_vehicle_count_on_peak = traffic_info['light_vehicle_count_on_peak']
        self.heavy_vehicle_count_on_peak = traffic_info['heavy_vehicle_count_on_peak']
        self.average_speed_off_peak = traffic_info['average_speed_off_peak']
        self.average_speed_on_peak = traffic_info['average_speed_on_peak']
        self.max_speed_off_peak = traffic_info['max_speed_off_peak']
        self.max_speed_on_peak = traffic_info['max_speed_on_peak']

        # defining class methods

    def get_road_id(self):
        return self.road_id

    def get_road_type(self):
        return self.road_type

    def get_road_type_for_query(self):
        # dirty hack to treat railroads as heavy car roads when making insert queries
        if self.road_type == 99:
            return 56
        return self.road_type

    def get_start_point(self):
        return self.start_point

    def get_end_point(self):
        return self.end_point

    def get_geom(self):
        return self.geom

    def is_noisy(self):
        return True

    def get_light_vehicle_count_off_peak(self):
        return self.light_vehicle_count_off_peak

    def get_heavy_vehicle_count_off_peak(self):
        return self.heavy_vehicle_count_off_peak

    def get_light_vehicle_count_on_peak(self):
        return self.get_light_vehicle_count_on_peak

    def get_heavy_vehicle_count_on_peak(self):
        return self.heavy_vehicle_count_on_peak

    def get_average_speed_off_peak(self):
        return self.average_speed_off_peak

    def get_average_speed_on_peak(self):
        return self.average_speed_on_peak

    def get_max_speed_off_peak(self):
        return self.max_speed_off_peak

    def get_max_speed_on_peak(self):
        return self.max_speed_on_peak
