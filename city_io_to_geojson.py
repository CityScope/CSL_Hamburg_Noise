#!/usr/bin/env python2.7

import CityScopeTable
import GridCell
import json
from shapely.geometry import Point, Polygon


def create_grid_of_cells(table):
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table.get_table_row_count()):
        for column in range(table.get_table_column_count()):
            cell_id = row * table.get_table_column_count() + column
            cell_info = table.get_result()['grid'][cell_id]
            cell_type = cell_info[0]
            cell_height = cell_info[1]

            # get coordinates of the current cell's origin
            if (row == 0 and column == 0):
                cell_origin = table.get_start_cell_origin_epsg()
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
                cell_type,
                cell_height
            )

            grid_of_cells.append(cell)

    return grid_of_cells


def get_cell_polygon_coord(cell):
    return [
        [
            cell.get_origin().y,
            cell.get_origin().x
        ],
        [
            cell.get_upper_right_corner().y,
            cell.get_upper_right_corner().x
        ],
        [
            cell.get_lower_right_corner().y,
            cell.get_lower_right_corner().x
        ],
        [
            cell.get_lower_left_corner().y,
            cell.get_lower_left_corner().x
        ]
    ]


def create_buildings_json(grid_of_cells):
    geo_json = {
    "type": "FeatureCollection",
      "features": [
        ]
    }

    buildings_id = 0
    for cell in grid_of_cells:
        # filter out empty cells
        if cell.get_cell_type() != -1:
            cell_geometry = {
                "geometry": {
                "type": "Polygon",
                "coordinates": [[]]
                }
            }
            cell_properties = {
                "properties": {
                    "height": cell.get_height(),
                    "type": cell.get_cell_type(),
                    # TODO : consider ignoring empty cells, distinguish between streets and buildings, ..
                  }
            }
            cell_id = {"id": buildings_id}
            buildings_id += 1

            for point in get_cell_polygon_coord(cell):
                cell_geometry["geometry"]["coordinates"][0].append(point)

            geo_json['features'].append(cell_geometry)
            geo_json['features'].append(cell_properties)
            geo_json['features'].append(cell_id)

    return geo_json


test_city_scope_address = 'https://cityio.media.mit.edu/api/table/mocho'
table = CityScopeTable.CityScopeTable(test_city_scope_address)
grid_of_cells = create_grid_of_cells(table)
geo_json = create_buildings_json(grid_of_cells)

# save geojson
with open('input_geojson/design/buildings' + '/' + 'buildings' + '.json', 'wb') as f:
    json.dump(geo_json, f)
