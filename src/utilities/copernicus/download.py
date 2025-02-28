import sys
import os
from pyprojroot.here import here
import boto3
from pathlib import Path

## TARGETS:
# NDVI (1km from 1999 or 300m from 2014)
# Green fraction (1km from 1999 or 300m from 2014)
# Photsynthetically active portion (check availability)
# Soil moisture (only from 2014 @ 300m)

# think this is the link:
#https://documentation.dataspace.copernicus.eu/Data/ComplementaryData/CLMS.html

def download_copernicus(bucket, product: str, target: str = "") -> None:
    """
    Downloads every file in bucket with provided product as prefix

    Raises FileNotFoundError if the product was not found

    Args:
        bucket: boto3 Resource bucket object
        product: Path to product
        target: Local catalog for downloaded files. Should end with an `/`. Default current directory.
    """

    #establish connection and session with auth
    session = boto3.session.Session()
    s3 = boto3.resource(
        's3',
        endpoint_url='https://eodata.dataspace.copernicus.eu',
        aws_access_key_id=os.environ['COPERNICUS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['COPERNICUS_SECRET'],
        region_name='default'
    )  # generated secrets
    
    #set target files and download
    files = bucket.objects.filter(Prefix=product)
    if not list(files):
        raise FileNotFoundError(f"Could not find any files for {product}")
    for file in files:
        os.makedirs(os.path.dirname(file.key), exist_ok=True)
        if not os.path.isdir(file.key):
            bucket.download_file(file.key, f"{target}{file.key}")