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

def get_sa_areas_masking_shapefile(scope, regions_list = None, name = None):
    
    #get base shapefile
    abs_region_path = here(f'data/SA_data_shapefiles/{scope}')
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
            target_file_dir = here(f'data/SA_data_shapefiles/{scope}_{name}_{date_string}.shp')
        else:
            target_file_dir = here(f'data/SA_data_shapefiles/{scope}_{date_string}.shp')

        # regions_list will include a set of sa codes based on the sa scope
        codes_in_shapefile = base_shapefile[sa_code_var_dict[scope]]

        # first subset removing strings that are not convertable to integers (i.e. 'zzzzz')
        def value_error_check(x):
            try:
                int(x)
                return x
            except:
                pass
        codes_in_shapefile = [value_error_check(x) for x in codes_in_shapefile]
        codes_in_shapefile = [x for x in codes_in_shapefile if x is not None]
        
        # create new subset of sa codes by checking for which are in regions_list
        codes_in_shapefile = [x for x in codes_in_shapefile if int(x) in regions_list]
        
        # subset the base_shapefile to the target regions
        mask = base_shapefile[sa_code_var_dict[scope]].isin(codes_in_shapefile)
        new_shapefile = base_shapefile[mask].to_file(target_file_dir)
    
    else:
        if name:
            target_file_dir = here(f'data/SA_data_shapefiles/{scope}_{name}_{date_string}.shp')
        else:
            target_file_dir = here(f'data/SA_data_shapefiles/{scope}_{date_string}.shp')

    # read in masking shapefile and return
    masking_shapefile = gpd.read_file(target_file_dir)
    
    return masking_shapefile    