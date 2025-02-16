## check for silo processed data by var/year

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

def check_silo_csv(var, year, month = None, day = None):
    dir_path = f'data/csv_data/{var}'
    if os.path.exists(os.path.join(dir_path)):
        # years is possible file listing in the head dir
        file_path = f'data/csv_data/{var}/{year}.csv'
        if os.path.exists(file_path):
            check = True
        else:
            # else check for years as it's own sub-directory
            dir_path = f'data/csv_data/{var}/{year}'
            if os.path.isdir(os.path.join(dir_path)):
                # years subdir is present - check for files present
                files = os.listdir(dir_path)
                ## months and days will be downloaded all together (they exist in the same record on silo)
                # So just need to check for .csvs and print a log of what is present
                if files:
                    check = True
                    print(f'files present in silo var {var} for {year}:\n')
                    print(files)
                else:
                    check = False
                    print(f'dir but not files present for silo var {var} for {year}, proceeding to download from silo')
            else:
                check = False
                print(f' dir for silo var {var} present but no year files or subdirs for {year}, proceeding to download from silo')
    else:
        check = False
        print(f'no processed data for silo var {var}, proceeding to download')
    return check