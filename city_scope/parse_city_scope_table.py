#!/usr/bin/env python2.7

# library imports
import os
import json
import configparser
from shapely.geometry import Polygon, mapping
from shapely.ops import cascaded_union
from config_loader import get_config

# local imports
import CityScopeTable
import GridCell


# creates a list of cells with spatial properties and CityScope information
def create_grid_of_cells(table):
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table.get_table_row_count()):
        for column in range(table.get_table_column_count()):
            cell_id = row * table.get_table_column_count() + column
            cell_content = table.get_result()['grid'][cell_id]
            cell_type = cell_content[table.table_cell_content.index("type")]
            cell_rotation = cell_content[table.table_cell_content.index("rotation")]

            # get coordinates of the current cell's origin
            if (row == 0 and column == 0):
                cell_origin = table.get_projected_start_cell_origin()
            # in highest row of grid - move towards the right
            elif (row == 0 and column != 0):
                cell_origin = grid_of_cells[(column - 1)].get_upper_right_corner()
            # the origin of the cell is always the equal to the lower left corner of the cell above
            else:
                cell_origin = grid_of_cells[cell_id - table.get_table_column_count()].get_lower_left_corner()

            cell = GridCell.GridCell(
                cell_origin,
                table.get_table_rotation(),
                table.get_table_cell_size(),
                cell_id,
                cell_type,
                cell_rotation,
            )

            grid_of_cells.append(cell)

    return grid_of_cells


# order of coordinates following right hand rule
def get_cell_polygon_coord(cell):
    return [
        [
            cell.get_origin().x,
            cell.get_origin().y
        ],
        [
            cell.get_lower_left_corner().x,
            cell.get_lower_left_corner().y
        ],
        [
            cell.get_lower_right_corner().x,
            cell.get_lower_right_corner().y
        ],
        [
            cell.get_upper_right_corner().x,
            cell.get_upper_right_corner().y
        ],
        # coordinates of a polygon need to form a closed linestring
        [
            cell.get_origin().x,
            cell.get_origin().y
        ],
    ]

# Returns a geojson containing all buildings as polygons
def create_buildings_json(table, grid_of_cells):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
        ]
    }

    buildings_id = 0
    for cell in grid_of_cells:
        # filter out empty or irrelevant cells
        if table.get_table_mapping()[cell.get_cell_type()]["type"] == "building":
            coordinates = []
            for point in get_cell_polygon_coord(cell):
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

# merges adjacent buildings and creates a multipolygon containing all buildings
def merge_adjacent_buildings(geo_json):
    polygons = []
    for feature in geo_json['features']:
        polygons.append(Polygon(feature['geometry']['coordinates'][0]))

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": mapping(cascaded_union(polygons)),
                "properties": {}
            }
        ]
    }


# collects the data from city io, transforms into a geojson and saves that geojson as input for the noise calculation
def save_buildings_from_city_scope():
    config = get_config()

    city_scope_address = config['CITY_SCOPE']['TABLE_URL_INPUT']
    # if the table origin is flipped to teh southeast, instead of regular northwest
    table_flipped = config['CITY_SCOPE'].getboolean('TABLE_FLIPPED')

    # dynamic input data from designer
    table = CityScopeTable.CityScopeTable(city_scope_address, table_flipped)
    grid_of_cells = create_grid_of_cells(table)
    geo_json = create_buildings_json(table, grid_of_cells)
    geo_json_merged = merge_adjacent_buildings(geo_json)

    # save geojson
    with open(config['NOISE_SETTINGS']['INPUT_JSON_BUILDINGS'], 'wb') as f:
        json.dump(geo_json_merged, f)


if __name__ == "__main__":
    save_buildings_from_city_scope()