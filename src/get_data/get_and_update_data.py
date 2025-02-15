### head script to check for data updates and refresh if available
# checks for years provided in silo data and for presence of ABS statistical area shape data
# downloads if not present

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

#custom modules
from utilities.spatial.get_silo_data import get_silo_data
from utilities.spatial.get_abs_data import get_abs_data
from src.utilities.delete_zip import delete_zip

def check_and_update_silo_data(varname, year):
    
    
            

    #if vartype == 'ndvi':

    #if vartype == 'bom':

    

    return return_string
    
                

