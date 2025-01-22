import os
import sys
import pathlib
from pyprojroot.here import here

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

### Obtains the monthly rainfall data from the silo db

# silo prefix  
prefix = 'Official/annual/monthly_rain/'

def get_monthly_rainfall(save_path, year_range = [2000,2022]):
    
    # Loop through the years
    for year in range(2000 , 2011):
        file_key = f'{prefix}{year}.monthly_rain.nc'
        local_file_path = os.path.join(dir_local, f'{year}.monthly_rain.nc')
        
        try:
            s3.download_file(bucket, file_key, local_file_path)
            print(f'Successfully downloaded {local_file_path}')
        except NoCredentialsError:
            print('Please provide valid AWS credentials')
        except Exception as e:
            print(f'Error downloading {local_file_path}: {e}')