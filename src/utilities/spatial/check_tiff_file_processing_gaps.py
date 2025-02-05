
#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import glob

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
    
    
