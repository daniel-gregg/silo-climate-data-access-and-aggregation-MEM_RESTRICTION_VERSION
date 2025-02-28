# returns all sa codes for a particular scope

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path
import pandas as pd

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

def get_sa_codes(sa_scope):

    #read in sa codes file
    sa_codes_df = pd.read_csv(here('data/other_data/sa_area_code_designations.csv'))
    headers = {
        'sa1' : 'SA1_MAINCODE_2016',
        #SA1_7DIGITCODE_2016
        'sa2' : 'SA2_MAINCODE_2016',
        #SA2_5DIGITCODE_2016
        #SA2_NAME_2016
        'sa3' : 'SA3_CODE_2016',
        #SA3_NAME_2016
        'sa4' : 'SA4_CODE_2016'
        #SA4_NAME_2016
        #GCCSA_CODE_2016
        #GCCSA_NAME_2016
        #STATE_CODE_2016
        #STATE_NAME_2016
        #AREA_ALBERS_SQKM
    }
    
    #access target sa_codes with headers dict reference
    sa_codes = set(sa_codes_df[headers[sa_scope]])

    return sa_codes