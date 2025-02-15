# Function to read in the .nc files and convert to tiff with ABS masking

## Set up

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# local utilities
from src.utilities.spatial.process_tiff_files import process_tiff_files
from src.utilities.spatial.check_tiff_file_processing_gaps import check_tiff_file_processing_gaps

def generate_spatial_data():
    
    # Check existence of processed Tiffs/Zonal statistics
    ## Function returns a list of data for processing to tiffs by checking date/varname correspondences
    data_lists = check_tiff_file_processing_gaps()

    # switch block to decide what to do next and call relevant functions
    if not data_lists['files_already_processed']:
        print('no processed files found')
    else:
        print('found the following files already processed\n')
        #print(f'{data_lists["files_already_processed"]}')
    if data_lists['files_to_process']:
        print(f'found {len(data_lists['files_to_process'])} files to process\n')
        user_input = input('Do you want to see the list of files to process? (yes/no)')
        if user_input.lower == 'yes' or user_input.lower() == 'y':
            print(f'{data_lists['files_to_process']}\n')
        process_tiff_files(data_lists['files_to_process'])
    else:
        print('all files up-to-date, exiting process')

