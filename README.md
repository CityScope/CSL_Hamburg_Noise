# CityScope NoiseModelling

This project is a fork of https://github.com/Ifsttar/NoiseModelling

## Requirements
- numpy
- geomet
- psycopg2

For conversion of shapefiles into geoJson
- ogr, from GDAL pip install GDAL==2.2.2 
(troubles installing = https://gis.stackexchange.com/questions/28966/python-gdal-package-missing-header-file-when-installing-via-pip)

## Input data
The computation is based on the geojson files in the `input_geojson` directory. 
Geojsons can be derived from the shapefiles in the `input_shape` directory using the `shp_to_geojson.py` script.
## The input data is classified into 2 categories
- 1 static input data: upper main road, lower main road and railroad 
   these are fix inputs of the noise environment that cannot be changed in competition entries
- 2 design input data: the proposed road network and the proposed buildings
    these are inputs made by the architects with their competition entries
    
## Start the H2 database and orbisGIS server server

Run  `java -cp "bin/*:bundle/*:sys-bundle/*" org.h2.tools.Server -pg` inside the project folder

## Computation
Start the computation by executing `noisemap.py`
The noise propgation will be computed based on the input files in the the `input_geojson directory`
The computation results will be saved in the `results` directory. Currently the output format is as shapefile.
Use QGis to view results (output style: choose categorize, magma (inverted) for best view)
Or drag and drop into https://mapshaper.org/

Chose computation options in sql_query_builder.py file

Chose the option of input detail
include_rail_road = False
include_lower_main_road = False
upper_main_road_as_multi_line = False # MultiLineStrings seems to deliver more accurate results but need more computation time

# Increase computation speed?
we should investigate whether we can provide a static information on sound sources from traffic data 
(or a set of options) so that this part doesn't have to be recomputed every time
https://github.com/Ifsttar/NoiseModelling/wiki/02-Quick-Start#compute-the-global-sound-level-of-light-and-heavy-vehicles

## Further help

https://github.com/Ifsttar/NoiseModelling/wiki