
#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import glob

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

def get_data_source_paths_as_dicts():
    climate_variable_paths = {x: [here((f'data/climate_data/{x}/{y}')) for y in os.listdir(f'data/climate_data/{x}')] for x in os.listdir(here('data/climate_data'))}
    abs_sa_data_paths = {x: glob.glob(f'data/SA_data_shapefiles/{x}/*.shp') for x in os.listdir('data/SA_data_shapefiles')}

    return {
        'climate_variable_paths' : climate_variable_paths,
        'abs_sa_data_paths' : abs_sa_data_paths
    }