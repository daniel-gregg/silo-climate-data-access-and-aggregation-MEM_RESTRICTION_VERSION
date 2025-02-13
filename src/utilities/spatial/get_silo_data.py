## Gets silo data from amazon s3

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
from src.utilities.aws_boto3.boto3_session import get_boto3_session
from utilities.spatial.get_vars_dict_mapping import get_vars_dict_mapping

def get_silo_data(var, years):

    # create session
    s3_session = get_boto3_session()
    bucket = 'silo-open-data'

    # check data and return dict for accessing boto3 data
    silo_vars_all = get_vars_dict_mapping() #mapping for all available silo vars from varnames to boto3 filenames (not including prefix and year/month/day)
    
    target_subdir = here(f'data/silo/{var}')
    if not os.path.isdir(target_subdir):
        #create directory
        Path(target_subdir).mkdir(parents=True, exist_ok=True)

    #access boto3 data
    for year in years:
        file_target = f'Official/annual/{silo_vars_all[var]}/{year}.{silo_vars_all[var]}.nc'
        target_save_path = os.path.join(target_subdir, f'{year}.nc')

        if not (f'{year}.nc') in os.listdir(target_subdir):
            # only download if it doesn't exist
            print(f'downloading {var} for {year}')
            try:
                s3_session.download_file(bucket, file_target, target_save_path)
                print(f'Successfully downloaded {var} for year {year}')
            except NoCredentialsError:
                print('Please provide valid AWS credentials')
            except Exception as e:
                print(f'Error downloading {var} for year {year} : {e}')
        else:
            print(f'{var} for {year} already exists in your directory - continuing to next')
        