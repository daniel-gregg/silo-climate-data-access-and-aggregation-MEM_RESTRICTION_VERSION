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

# local modules
from src.get_data.get_and_update_data import get_and_refresh_data
from src.utilities.spatial.get_abs_data import get_abs_data
from src.utilities.delete_zip import delete_zip
from src.utilities.spatial.get_silo_data import get_silo_data
from src.utilities.spatial.get_zonal_statistics_and_rasters_silo_vars import get_zonal_statistics_and_rasters_silo_vars
from src.utilities.spatial.delete_silo_raw_data import delete_silo_raw_data

### setup
target_data_dict = user_selected_data_dict()
name = 'sgr_test' #optional name for the run - saved with final .csv//tif filenames generated

### Check for masking file data (statistical area shapefiles)
sa_scope_list = target_data_dict['statistical_areas']
get_abs_data(sa_scope_list)
# delete any zipfiles that are present
delete_zip()

### Get silo variables and map to rasters/csvs for selected regions
silo_vars_dict = target_data_dict['silo_climate_vars']
for var in silo_vars_dict.keys():
    var_years = silo_vars_dict[var]
    get_silo_data(var, years)
    get_zonal_statistics_and_rasters_silo_vars(var, name)
    delete_silo_raw_data(var)

### Get other vars and map to rasters/csvs for selected regions

