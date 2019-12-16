# CityScope NoiseModelling

This project is a fork of https://github.com/Ifsttar/NoiseModelling

## Requirementsvisvalingamwyatt
- pyshp
- geomet
- shapely
- psycopg2
- numpy
- requests

For conversion of shapefiles into geoJson
- ogr, from GDAL pip install GDAL==2.2.2 
(troubles installing = https://gis.stackexchange.com/questions/28966/python-gdal-package-missing-header-file-when-installing-via-pip)

## Input data
The computation is based on the geojson files in the `input_geojson` directory. 
Geojsons can be derived from the shapefiles in the `input_shape` directory using the `shp_to_geojson.py` script.
## The input data is classified into 2 categories
- 1 static input data in input_geosjon/static/roads: roads_network.json, railroads.json
   these are fix inputs of the noise environment that cannot be changed in competition entries
- 2 design input data: The proposed buildings as geojson. Will be generated from cityScope grid
    
## Run as noise module as docker 
If not installed yet: run ' sh ./install_docker.sh'
If already installed run ' sh ./docker/run_docker.sh'

## Start the CityScope noise module without docker

Run 'start_noise_module.sh'

## Config.ini
Chose the option of input detail
include_rail_road = False
include_lower_main_road = False
upper_main_road_as_multi_line = False # MultiLineStrings seems to deliver more accurate results but need more computation time

Chose your usage_mode 
city_scope : Reads the grid of a cityIO endpoint and calculates results for the grid, posts results
tuio: Reads the input file in for the buildings.json 

## Computation
Start the computation by executing `noisemap.py`
The noise propgation will be computed based on the input files in the the `input_geojson directory`
The computation results will be saved in the `results` directory. Currently the output format is as shapefile.
Use QGis to view results (output style: choose categorize, magma (inverted) for best view)
Or drag and drop into https://mapshaper.org/

# Increase computation speed?
we should investigate whether we can provide a static information on sound sources from traffic data 
(or a set of options) so that this part doesn't have to be recomputed every time
https://github.com/Ifsttar/NoiseModelling/wiki/02-Quick-Start#compute-the-global-sound-level-of-light-and-heavy-vehicles

## Further help

https://github.com/Ifsttar/NoiseModelling/wiki


## Input & Output illustration
The input is divided into static inputs and design inputs. 
Static inputs are globally set and not possible to be altered by city scope user
Design inputs are expected from city scope user.
###The input is divided into static inputs 
1) upper main road 
    a) detailed version of upper main road as MultiLineString (red) [more detailed restuls, longer computation]
    b) simple version of upper main road as LineString (green) [slighty less detailed results, faster compfutation]
2) lower main road (blue)
3) railroad (red dots)

Choose your input options in the sql_query_builder

![static inputs](https://github.com/CityScope/CSL_Hamburg_Noise/blob/master/documentation/static_input_options.png)

###Design inputs
those are the inputs we are expectiong from the architect user. 
Road network (not mandatory) and buildings

![static and design inputs](https://github.com/CityScope/CSL_Hamburg_Noise/blob/master/documentation/static_and_design_input.png)

###Results
*Results example with mock-traffic input*
Result interpretation:
 
EU treshold for "relevant" noise is 55db

 < 45 dB(A) ’ WHERE IDISO=0

 45 <> 50 dB(A) ’ WHERE IDISO=1
 
 50 <> 55 dB(A) ’ WHERE IDISO=2
 
 55 <> 60 dB(A) ’ WHERE IDISO=3
 
 60 <> 65 dB(A) ’ WHERE IDISO=4
 
 65 <> 70 dB(A) ’ WHERE IDISO=5
 
 70 <> 75 dB(A) ’ WHERE IDISO=6
 
 '>' 75 dB(A) ’ WHERE IDISO=7
 
 ![results](https://github.com/CityScope/CSL_Hamburg_Noise/blob/master/documentation/results.png)
