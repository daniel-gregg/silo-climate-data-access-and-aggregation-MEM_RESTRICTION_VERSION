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
    for paths in os.listdir(here('data')):
        zipfiles_list = glob.glob(f'data/{paths}/*.zip')
        for sub_folder in [foldername for foldername in os.listdir(here(f'data/{paths}')) if os.path.isdir(os.path.join(f'data/{paths}', foldername))]:
            zipfiles_list.extend(glob.glob(f'data/{paths}/{sub_folder}/*.zip'))
            
    for file in zipfiles_list:
        print(f'removing {file} from /data')
        os.remove(file)