#!/usr/bin/env python2.7

import convert as conv

shp_path_buildings = '/home/andre/noise_new/modelling/input_shape/buildings.shp'
shp_path_road_network = '/home/andre/noise_new/modelling/input_shape/road_network.shp'
shp_path_upper_main_road_single = '/home/andre/noise_new/modelling/input_shape/upper_part_main_road_single.shp'
shp_path_upper_main_road_multi = '/home/andre/noise_new/modelling/input_shape/upper_part_main_road.shp'
shp_path_lower_main_road_multi = '/home/andre/noise_new/modelling/input_shape/lower_part_main_road.shp'
shp_path_railroad = '/home/andre/noise_new/modelling/input_shape/railroad.shp'


def convert(input_file_path, json_dir, output_file_name):
    conv.convert(input_file_path, 'input_geojson/' + json_dir + '/' + output_file_name + '.json')


convert(shp_path_buildings, 'design/buildings', 'buildings')
convert(shp_path_road_network, 'design/roads', 'road_network')
convert(shp_path_upper_main_road_single, 'static/roads', 'upper_main_road_single')
convert(shp_path_upper_main_road_multi, 'static/roads', 'upper_main_road_multi')
convert(shp_path_lower_main_road_multi, 'static/roads', 'lower_main_road_multi')
convert(shp_path_railroad, 'static/roads', 'railroad')
print("successfully processed")
