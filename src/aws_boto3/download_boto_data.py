import sys
import os
from pyprojroot.here import here
from src.aws_boto3.create_session import session
from src.utilities.silo_vars import silo_vars
import boto3
from pathlib import Path

############# data available:

# see here for available data, short-names, and definitions:
#https://www.longpaddock.qld.gov.au/silo/about/climate-variables/

#############################


## Setting things up

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# create session and define local variables for use in downloading data
session = boto3.Session(
    aws_access_key_id = os.environ['IAM_USER_ACCESS_KEY'],
    aws_secret_access_key = os.environ['IAM_USER_ACCESS_PASSWORD']
    )

s3 = session.client('s3')
bucket = 'silo-open-data'

# set target path for bulk datasets
target_dir = os.path.join('data', 'climate_data')
if not os.path.isdir(target_dir):
    Path(target_dir).mkdir(parents=True, exist_ok=True)

# loop through years and aggregate according to model

get_monthly_rainfall(target_dir, year)
get_daily_rainfall()
get_morton_actual_evapotranspiration()
get_morton_potential_evapotranspiration()
get_morton_wet_area_potential_evapotranspiration()
get_radiation()
get_max_temp()
get_min_temp()
get_vapour_pression()
get_vapour_pressure_deficit()
get_pan_evaporation_class_a()
get_syntehtic_evaporation() #preferred to class a due to declining stations using class a type evaporation
get_morton_shallow_lake_evaporation()
get_relative_humidity_at_max_temp()
get_relative_humidity_at_min_temp()
get_FAO_evapotranspiration_short_crop()
get_ASCE_evapotranspiration_tall_crop()
get_mean_sea_level_atmospheric_pressure()


get_temperature()


# define target data destination for raw data

raw_data_endpoint = '/data'

## Get data and save to 
