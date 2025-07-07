import sys
import os
from pyprojroot.here import here
import boto3
from pathlib import Path

############# data available:

# see here for available data, short-names, and definitions:
#https://www.longpaddock.qld.gov.au/silo/about/climate-variables/

#############################


## Setting things up
def get_silo_boto3_session():

    # create session and define local variables for use in downloading data
    session = boto3.Session(
        aws_access_key_id = os.environ['SILO_ACCESS_KEY_ID'],
        aws_secret_access_key = os.environ['SILO_SECRET_KEY'],
        region_name = 'ap-southeast-2'
        )

    s3_session = session.client('s3')

    return s3_session

# set target path for bulk datasets
target_dir = os.path.join('data', 'climate_data')
if not os.path.isdir(target_dir):
    Path(target_dir).mkdir(parents=True, exist_ok=True)

# loop through years and aggregate according to model
