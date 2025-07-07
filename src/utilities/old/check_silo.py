## check for silo processed data by var/year

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import pandas as pd

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
        target_dir = f'data/csv_data/{name}/{var}'
        file_dir = f'data/csv_data/{name}/{var}.csv'
    else:
        target_dir = f'data/csv_data/{var}'
        file_dir = f'data/csv_data/{var}.csv'

    if not os.path.exists(target_dir):
        # file does not exist so no data
        check = False
    else:
        #read file
        df = pd.read_csv(file_dir)

        #subset for year:
        sub_df = df[df['year']==year,]

        # if empty, no data for that year present.
        if sub_df.empty:
            check = False
        else:
            check = sub_df.shape[0] #return number of rows
    
    return check

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