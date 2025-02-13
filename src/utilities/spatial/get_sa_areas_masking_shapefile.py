## returns a shapefile object with subsetting of the base masking file based on selected regions

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import geopandas as gpd
from datetime import datetime, date

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

def get_sa_areas_masking_shapefile(sa_scope, regions_list = None, name = None):
    
    #get base shapefile
    abs_region_path = here(f'data/SA_data_shapefiles/{sa_scope}')
    base_shapefile = gpd.read_file(abs_region_path)

    sa_code_var_dict = {
        'sa1' : 'SA1_CODE21',
        'sa2' : 'SA2_CODE21',
        'sa3' : 'SA3_CODE21',
        'sa4' : 'SA4_CODE21',
    }

    #format target filename
    date_string = "{:%Y_%m_%d}".format(datetime.now())
    
    # subset based on regions
    if regions_list:

        if name:
            target_file_dir = here(f'data/SA_data_shapefiles/{sa_scope}_{name}_{date_string}.shp')
        else:
            target_file_dir = here(f'data/SA_data_shapefiles/{sa_scope}_{date_string}.shp')

        # regions_list will include a set of sa codes based on the sa scope
        codes_in_shapefile = base_shapefile[sa_code_var_dict[sa_scope]]

        # create new shapefile with subset
        base_shapefile[codes_in_shapefile in regions_list].to_file(target_file_dir)
    
    else:
        if name:
            target_file_dir = here(f'data/SA_data_shapefiles/{sa_scope}_{name}_{date_string}.shp')
        else:
            target_file_dir = here(f'data/SA_data_shapefiles/{sa_scope}_{date_string}.shp')

    # read in masking shapefile and return
    masking_shapefile = gpd.read_file(target_file_dir)
    
    return masking_shapefile    