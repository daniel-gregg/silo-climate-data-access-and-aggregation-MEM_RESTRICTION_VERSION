
#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import pandas as pd
import glob
import time

from data import user_selected_data_dict

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

def check_silo_csv(var, year, name = None):
    # first get target for var
    #target_data = user_selected_data_dict()['silo'][var] # an array of years for var

    # check if dir exists
    if name:
        file_dir = f'data/csv_data/{name}/{var}/{year}.csv'
    else:
        file_dir = f'data/csv_data/{var}/{year}.csv'

    if not os.path.exists(file_dir):
        # file does not exist so no data
        check = False
    else:
        #read file
        check = True
    
    return check


def delete_raw_csvs(var, name = None):
    # first get target for var
    #target_data = user_selected_data_dict()['silo'][var] # an array of years for var

    # check if dir exists
    if name:
        dirpath = f'data/csv_data/{name}/{var}'
    else:
        dirpath = f'data/csv_data/{var}'

    files_list = os.listdir(here(dirpath))

    for file in files_list:
        os.remove(here(f'data/csv_data/{name}/{var}/{file}'))

def check_silo_tiff(var, years, name = None):
    # first get target for var
    #target_data = user_selected_data_dict()['silo'][var] # an array of years for var

    if name:
        dir_path = f'data/tiff_files/{name}/{var}'
    else:
        dir_path = f'data/tiff_files/{var}'
    if os.path.exists(os.path.join(dir_path)):
        # check which years present
        file_list = os.listdir(dir_path)
        years_list = [int(x.split(".")[0]) for x in file_list]
        missing_years = [x for x in years if x not in years_list]
    else:
        missing_years = years

    return missing_years


def get_vars_dict_mapping():
    vars_dict = {
        'silo' : {
            'monthly_rainfall' : 'monthly_rain',
            'daily_rainfall' : 'daily_rain',
            'morton_actual_evapotranspiration' : 'et_morton_actual',
            'morton_potential_evapotranspiration' : 'et_morton_potential',
            'morton_wet_area_potential_evapotranspiration' : 'et_morton_wet',
            'max_temp' : 'max_temp',
            'min_temp' : 'min_temp',
            'vapour_pressure' : 'vp',
            'vapour_pressure_deficit' : 'vp_deficit',
            'pan_evaporation_class_a' : 'evap_pan',
            'synthetic_evaporation' : 'evap_syn',
            'combination_evaporation' : 'evap_comb',
            'morton_shallow_lake_evaporation' : 'evap_morton_lake',
            'relative_humidity_at_max_temp' : 'rh_tmax',
            'relative_humidity_at_min_temp' : 'rh_tmin',
            'FAO_evapotranspiration_short_crop' : 'et_short_crop',
            'ASCE_evapotranspiration_tall_crop' : 'et_tall_crop',
            'mean_sea_level_atmospheric_pressure' : 'mslp',
            'solar_radiation' : 'radiation'
        }, 
        'ndvi' : {},
        'bom' : {},
    }

    return vars_dict

def delete_zip():
    ## look in all data files and list file paths that include '.zip' at the end
    for path in os.listdir(here('data')):
        zipfiles_list = glob.glob(f'data/{path}/*.zip')
        # remove any non-folder paths
        if not os.path.isdir(os.path.join(f'data/{path}')):
            continue
        if zipfiles_list:
            for sub_folder in [foldername for foldername in os.listdir(here(f'data/{path}')) if os.path.isdir(os.path.join(f'data/{path}', foldername))]:
                zipfiles_list.extend(glob.glob(f'data/{path}/{sub_folder}/*.zip'))
                
    for file in zipfiles_list:
        print(f'removing {file} from /data')
        os.remove(file)

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

#Iterator to yield key paths for the filenames dict
def key_paths(obj):

    for key, value in obj.items():
        if isinstance(value, dict):
            yield from (f'{key}.{sub}' for sub in key_paths(value))
        else:
            yield key


def get_unknown_nested_dict_val(d_key_list, d):
    for key in d_key_list:
        if isinstance(d[key], dict):
            return get_unknown_nested_dict_val(d_key_list[1:], d[key])
        else:
            return d[key]
    
def check_tiff_file_processing_gaps():
    ## Currently only checks for YEAR, not month (for monthly data)
    # nested dictionary for varname-sa_scope-year

    # get dict of sa_scope-varname-year targets from data/climate_data 
    sa_scopes = os.listdir('data/SA_data_shapefiles')

    #check for zipfiles in sa_scopes (should be removed but this acts as an additional check to avoid errors)
    zipfiles_list = glob.glob(f'data/SA_data_shapefiles/*.zip')
    if zipfiles_list:
        for sa_scope in sa_scopes:
            if sa_scope in zipfiles_list:
                sa_scopes = sa_scopes.remove(sa_scope)
    
    # initialise dict
    sascope_varname_year_processed_data_present_dict = {}

    # loop and create booleans for the sa-scope_varname_year dict
    for sa_scope in os.listdir('data/SA_data_shapefiles'):
        
        # get varnames
        varnames = os.listdir(here('data/climate_data'))
        
        # get years
        for varname in varnames:
            years = os.listdir(here(f'data/climate_data/{varname}'))
            # remove '.nc' from the end
            years = {year.rsplit(".", 1)[0]: False for year in years}

            # convert False to True for present data
            tiff_path = here(f'data/tiff_files/{varname}')
            if os.path.exists(tiff_path):
                for year in years.keys():
                    if os.path.exists(here(f'data/tiff_files/{varname}/{year}.tiff')):
                        years[year] = True
        
            # combine into sub-dictionary
            sub_dict = {var: years for var in varnames}

            # add to final dict for each var
            sascope_varname_year_processed_data_present_dict[sa_scope] = sub_dict

    all_files_list = []
    for path in key_paths(sascope_varname_year_processed_data_present_dict):
        all_files_list.append(path)

    files_to_process = []
    files_already_processed = []

    ### Create list of already processed (true) and missing files (false)
    for file in all_files_list:
        file_present = get_unknown_nested_dict_val(file.split('.'), sascope_varname_year_processed_data_present_dict)
        if file_present:
            files_already_processed.append(file)
        else:
            files_to_process.append(file)

    return {
        'files_already_processed' : files_already_processed,
        'files_to_process' : files_to_process
    }
    
def delete_silo_raw_data(var, year, name = None):
    
    time.sleep(5)
    
    # delete nc file
    file = os.path.join(here(f'data/silo/{var}/{year}.nc'))
    print(f'removing {file} from /data')
    os.remove(file)

    # find and delete tiff files
    if name:
        filelist = os.listdir(here(f'data/tiff_files/{name}/{var}'))
        for file in filelist:
            try:
                os.remove(here(f'data/tiff_files/{name}/{var}/{file}'))
            except:
                continue
    else:
        filelist = os.listdir(here(f'data/tiff_files/{var}'))
        for file in filelist:
            try:
                os.remove(here(f'data/tiff_files/{name}/{file}'))
            except:
                continue