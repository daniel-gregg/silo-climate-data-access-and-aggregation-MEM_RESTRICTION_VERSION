# Function to read in the .nc files and convert to tiff with ABS masking

## Set up

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import glob

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.utilities.spatial.get_zonal_statistics_and_rasters import get_zonal_statistics_and_rasters

#variables
climate_variable_paths = {x: [here((f'data/climate_data/{x}/{y}')) for y in os.listdir(f'data/climate_data/{x}')] for x in os.listdir(here('data/climate_data'))}
abs_sa_data_paths = {x: y for y in glob.glob(f'data/SA_data_shapefiles/{x}/*.shp') for x in os.listdir(f'data/SA_data_shapefiles')}

#loop through nc_data_paths and the abs_sa_shapefiles dictionaries to generate tiffs and zonal/period statistics
for climate_var in climate_variable_paths:
    for sa_region in abs_sa_data_paths:
        get_zonal_statistics_and_rasters(
            climate_var,
            sa_region
        )

## Get NC files list


## Read in NC files


## Check for existence of relevant tiff files


## Convert to TIFF


## Mask with shapefiles from ABS for statistical areas


## Calculate relevant zonal statistics


## Generate .csv files with target statistics

