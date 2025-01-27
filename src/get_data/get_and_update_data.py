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
from src.utilities.aws_boto3.get_silo_data import get_silo_data
from src.utilities.abs_sa_regions.get_abs_data import get_abs_data
from src.utilities.delete_zip import delete_zip

def get_and_refresh_data(
        years=[*range(2011,2023)],
        silo=[
            'monthly_rainfall',
            #'daily_rainfall',
            'morton_actual_evapotranspiration',
            'morton_potential_evapotranspiration',
            'morton_wet_area_potential_evapotranspiration',
            'max_temp',
            'min_temp',
            'vapour_pressure',
            'vapour_pressure_deficit',
            'pan_evaporation_class_a',
            'synthetic_evaporation',
            'relative_humidity_at_max_temp',
            'relative_humidity_at_min_temp',
            'FAO_evapotranspiration_short_crop',
            'ASCE_evapotranspiration_tall_crop',
            'mean_sea_level_atmospheric_pressure'
        ],
        abs=True,
        abs_subsets=[
            'sa1',
            'sa2',
            'sa3',
            'sa4']
    ):

    ## Get silo climate/weather data
    get_silo_data(years,silo)

    ## Get ABS data
    if abs:
        get_abs_data(subset = abs_subsets)
    
    ## delete pre-existing zip files in data if present
    delete_zip()
    
                

