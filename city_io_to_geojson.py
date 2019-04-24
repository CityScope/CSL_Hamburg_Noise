#!/usr/bin/env python2.7

import urllib
import GridCell
import geopy
import json

test_city_scope_address = 'https://cityio.media.mit.edu/api/table/mocho'
result = json.load(urllib.urlopen(test_city_scope_address))

start_cell_origin = geopy.Point(result['header']['spatial']['latitude'], result['header']['spatial']['longitude'])
table_rotation = result['header']['spatial']['rotation'] # TODO can the table rotation be different form the cell rotation??
table_cell_size = result['header']['spatial']['cellSize']
table_row_count = result['header']['spatial']['nrows']
table_column_count = result['header']['spatial']['ncols']


def create_grid_of_cells():
    # create a list of GridCell objects for all cells in grid
    grid_of_cells = []
    for row in range(table_row_count):
        for column in range(table_column_count):
            cell_id = row * table_column_count + column
            cell_info = result['grid'][cell_id]
            cell_type = cell_info[0]
            cell_height = cell_info[1]

            # get coordinates of the current cell's origin
            if (row == 0 and column == 0):
                cell_origin = start_cell_origin
            # in highest row of grid - move towards the right
            elif (row == 0 and column != 0):
                cell_origin = grid_of_cells[(column - 1)].get_upper_right_corner()
            # the origin of the cell is always the equal to the lower left corner of the cell above
            else:
                cell_origin = grid_of_cells[cell_id - table_column_count].get_lower_left_corner()

            cell = GridCell.GridCell(cell_origin, table_rotation, table_cell_size, cell_type, cell_height)
            grid_of_cells.append(cell)

    return grid_of_cells

def get_cell_polygon(cell):
    return [
        [
            cell.get_origin().latitude,
            cell.get_origin().longitude
        ],
        [
            cell.get_upper_right_corner().latitude,
            cell.get_upper_right_corner().longitude
        ],
        [
            cell.get_lower_right_corner().latitude,
            cell.get_lower_right_corner().longitude
        ],
        [
            cell.get_lower_left_corner().latitude,
            cell.get_lower_left_corner().longitude
        ]
    ]

def create_geo_json(grid_of_cells):
    geo_json = {
    "type": "FeatureCollection",
      "features": [
        ]
    }

    for cell in grid_of_cells:
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
        cell_id = {"id": 1}

        for point in get_cell_polygon(cell):
            #print(cell_geometry)
            cell_geometry["geometry"]["coordinates"][0].append(point)

        feature = [cell_geometry, cell_properties, cell_id]
        geo_json['features'].append(cell_geometry)
        geo_json['features'].append(cell_properties)
        geo_json['features'].append(cell_id)
        print("features", len(geo_json['features']))

    print (json.dumps(geo_json))

    return json.dumps(geo_json)


grid_of_cells = create_grid_of_cells()
print(len(grid_of_cells))
geo_json = create_geo_json(grid_of_cells)

exit()
with open('input_geojson/' + json_dir + '/' + output_file_name + '.json', 'wb') as f:
    json.dump(fc, f)
