## Head script that calls modules - aim to turn into API function in the future

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# import user-specified target data file
from data.user_selected_data_dict import user_selected_data_dict

# spatial functions
from src.utilities.spatial_utilities import get_abs_data
from src.utilities.spatial_utilities import get_silo_data
from src.utilities.spatial_utilities import process_silo_var

# data functions
from src.utilities.data_utilities import delete_zip
from src.utilities.data_utilities import delete_silo_raw_data
from src.utilities.data_utilities import check_silo_csv


### setup
target_data_dict = user_selected_data_dict()
name = 'sgr_test' #optional name for the run - saved with final .csv//tif filenames generated

### Check for masking file data (statistical area shapefiles)
sa_scope_list = target_data_dict['statistical_areas']
get_abs_data(sa_scope_list)
# delete any zipfiles that are present
delete_zip()

### check for silo data updates, download if needed and process by var-year to csv file
# Download Silo data and map to rasters for selected regions
silo_vars_dict = target_data_dict['silo']

for var in silo_vars_dict.keys():
    years = silo_vars_dict[var]
    
    for year in years:
        # check whether data already exists
        check = check_silo_csv(var, year, name)
        # returns true if data already present for var-year combination

        # print a warning if less than 12 records returned (indicates either an annual variable or part year only)
        if check and check < 12:
                print(f'Warning: only {check} records present for variable {var} in {year}')
    
        if not check:
            # data not present
            # download silo var/year data
            get_silo_data(var, year)

            # process to csv
            process_silo_var(var, year, name)

            # delete raw data to save harddrive space
            delete_silo_raw_data(var, year,name)


### Download other data
#TBD

### Process csv vars to get target final variables (e.g. rainfall intensity, monthly records, yearly records, etc)


