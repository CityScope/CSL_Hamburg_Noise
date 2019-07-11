#!/usr/bin/env python2.7

from city_io_to_geojson import city_io_to_geojson, CityScopeTable
import json
import configparser


def create_buildings_json(table, grid_of_cells):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }

    buildings_id = 0
    for cell in grid_of_cells:
        # filter out empty or irrelevant cells
        #if not table.get_table_mapping()[str(cell.get_cell_type())] in ['ROAD', 'unknown', '']:
        print(cell.get_cell_type())
        if not table.get_table_mapping()[cell.get_cell_type()] in ['street', 'unknown', '']:
            coordinates = []
            for point in city_io_to_geojson.get_cell_polygon_coord(cell):
                coordinates.append(point)

            cell_content = {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                },
                "properties": {
                    "id": buildings_id,
                    "rotation": cell.get_cell_rotation(),
                    "type": cell.get_cell_type(),
                },
                "id": buildings_id
            }

            buildings_id += 1

            geo_json['features'].append(cell_content)

    return geo_json


# collects the data from city io, transforms into a geojson and saves that geojson as input for the noise calculation
def save_buildings_from_city_scope():
    config = configparser.ConfigParser()
    config.read('config.ini')

    city_scope_address = config['CITY_SCOPE']['TABLE_URL_INPUT']
    # if the table origin is flipped to teh southeast, instead of regular northwest
    table_flipped = config['CITY_SCOPE'].getboolean('TABLE_FLIPPED')

    # dynamic input data from designer
    table = CityScopeTable.CityScopeTable(city_scope_address, table_flipped)
    grid_of_cells = city_io_to_geojson.create_grid_of_cells(table)
    geo_json = create_buildings_json(table, grid_of_cells)

    # save geojson

    with open(config['SETTINGS']['INPUT_JSON_BUILDINGS'], 'wb') as f:
        json.dump(geo_json, f)