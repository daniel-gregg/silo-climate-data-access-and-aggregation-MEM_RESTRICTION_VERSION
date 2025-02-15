#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import glob

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

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