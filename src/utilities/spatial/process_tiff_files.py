
#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from utilities.spatial.get_zonal_statistics_and_rasters_silo_vars import get_zonal_statistics_and_rasters_silo_vars

def process_tiff_files(files_to_process):
    
    # ask user for permission to proceed
    user_input = input("Do you want to continue? (yes/no): ")
    if user_input.lower() == "yes" or user_input.lower() == "y":
        print("Processing files ... (this may take some time)")
    else:
        print("Exiting...")
        return ()
    
    for file_name in files_to_process:
        raw_data_file_dir = file_name.split('.')
        file_dir_string = 'data/climate_data'
        for element in raw_data_file_dir:
            if element in os.listdir('data/SA_data_shapefiles'):
                sa_scope = element
                continue
            else:
                file_dir_string = file_dir_string + f'/{element}'
        
        # check file exists
        print(file_dir_string)
        if not os.path.exists(file_dir_string+'.nc'):
            return FileExistsError(f'file {file_dir_string} not found')
        
        # else move to obtaining zonal statistics and rasters
        get_zonal_statistics_and_rasters_silo_vars(file_dir_string, sa_scope)
   
    return 'done'



