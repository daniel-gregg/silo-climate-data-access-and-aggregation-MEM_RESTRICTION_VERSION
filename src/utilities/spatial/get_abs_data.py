### Accesses the Australian Bureau of Statistics website and downloads shape files (.shp) for SA (statistical area) boundaries
import zipfile
import urllib.request

import sys
import os
from pyprojroot.here import here
from pathlib import Path

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

def get_abs_data(sa_scope_list):

    # target directory
    target_dir = os.path.join('data', 'SA_data_shapefiles')
    #create path if it doesn't exist, leave if it does:
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    # Urls for ABS shape files for SA regions
    urls = {
        'sa1' : "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/",
        'sa2' : "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/",
        'sa3' : "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/",
        'sa4' : "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/"
    }

    # filenames (from the Urls above)
    filenames = {
        'sa1' : "SA1_2021_AUST_SHP_GDA94.zip",
        'sa2' : "SA2_2021_AUST_SHP_GDA94.zip",
        'sa3' : "SA3_2021_AUST_SHP_GDA94.zip",
        'sa4' : "SA4_2021_AUST_SHP_GDA94.zip"
    }

    # loop through and extract/save to directory
    for filename in filenames.keys():
        # check if SA distinction is a target (included in subsets)
        if filename in sa_scope_list:
            target_subdir = os.path.join('data', 'SA_data_shapefiles', filename)

            # check if exists
            if not os.path.isdir(target_subdir):
                print('downloading shapefile for ' + filename)
                print('bytes:')
                ## download and save zipfile
                response = urllib.request.urlopen(urls[filename]+filenames[filename])
                with open(target_dir + '/' + filenames[filename], "wb") as f:
                    f.write(response.read())
                print('\n')

                ## extract zipfile

                # first create folder if it doesn't exist:
                if not os.path.isdir(target_subdir):
                    Path(target_subdir).mkdir(parents=True, exist_ok=True)

                # extract to target subdir
                with zipfile.ZipFile(target_dir + '/' + filenames[filename]) as zip_file:
                    zip_file.extractall(target_subdir)
