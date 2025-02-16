# Function to read in the .nc files and convert to tiff with ABS masking

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

## Spatial modules/packages
import xarray as xr
import pandas as pd
import rasterio as rio 
from rasterstats import zonal_stats
from datetime import datetime, date

#local imports
from src.utilities.spatial.get_vars_dict_mapping import get_vars_dict_mapping
from src.utilities.spatial.get_sa_areas_masking_shapefile import get_sa_areas_masking_shapefile
from data.user_selected_data_dict import user_selected_data_dict

def get_zonal_statistics_and_rasters_silo_vars(var, name = ''):

    # get data targets
    target_data_dict = user_selected_data_dict()

    # get target silo vars from data dict
    silo_vars = target_data_dict['silo']

    # reference masking region statistical area scopes from data dict
    sa_scope = target_data_dict['statistical_areas']

    # set data paths
    years = silo_vars[var]

    # masking subsets - check if any specified
    masking_subsets_dict = target_data_dict['masking_subsets']

    #format target filename
    date_string = "{:%Y_%m_%d}".format(datetime.now())
    
    # first get scope
    for scope in sa_scope:

        if masking_subsets_dict:
            for subset in masking_subsets_dict.keys():
                # get the masking shapefile - this includes any subsets
                regions_list = masking_subsets_dict[subset](scope)
                masking_shapefile = get_sa_areas_masking_shapefile(scope, regions_list, name)

                # then years
                for year in years:    
                    data_var_path = here(f'data/silo/{var}/{year}.nc')
                    data_file = xr.open_dataset(data_var_path) #this is the 'ds_xxx' file in Yuan's original script
                    # lat is reversed so reindex
                    data_file = data_file.reindex(lat=list(reversed(data_file.lat)))

                    # get target varname recorded in the silo data file
                    varname_in_file = get_vars_dict_mapping()['silo'][var]
                    target_data = data_file[varname_in_file]

                    # set key values 
                    ymin = data_file.lat.max().values + (0.5 * 0.05)  # Adjust the origin to the upper left
                    xmin = data_file.lon.min().values - (0.5 * 0.05)
                    transform = (0.05, 0, xmin, 0, -0.05, ymin)  # GeoTransform for the TIFF
                    
                    #set metadata
                    meta = {'driver': 'GTiff',
                            'dtype': 'float32',
                            'transform': transform,
                            'width': target_data.sizes['lon'],
                            'height': target_data.sizes['lat'],
                            'count': 1,
                            'crs': 4326,
                            'nodata': -9999}

                    # get data values and periods
                    data_vals = target_data.values

                    if data_vals.shape[0] <=1:
                        record = year
                    if data_vals.shape[0] <=12:
                        record = ['jan', 'feb' ,'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                    if data_vals.shape[0]>360 and data_vals.shape[0]<370:
                        record = 'day'

                    # set period structure
                    for period in range(data_vals.shape[0]):
                        if record == year:
                            tiff_file_name = os.path.join(f'data/tiff_files/{var}_{year}_{name}_{date_string}.tif')
                        if type(record) == list:
                            tiff_file_name = os.path.join(f'data/tiff_files/{var}_{year}_{name}_{record[period]}_{date_string}.tif')
                        if record == 'day':
                            tiff_file_name = os.path.join(f'data/tiff_files/{var}_{year}_{name}_day {period+1}_{date_string}.tif')

                    # set tiff file path and make directory if it doesn't exist
                    Path(os.path.join('data','tiff_files')).mkdir(parents=True, exist_ok=True)

                    # get zonal stats from the tiff file
                    with rio.open(tiff_file_name, 'w', **meta) as dst:
                        dst.write(data_vals[period, :, :], 1)  # Save each month in a separate file
                
                        # Perform zonal statistics on the monthly TIFF
                    try:
                        masking_shapefile = masking_shapefile[~(masking_shapefile['geometry'].is_empty | masking_shapefile['geometry'].isna())]
                        stats = zonal_stats(masking_shapefile, tiff_file_name, stats=['mean', 'min', 'max'], nodata=-9999, geojson_out=True, all_touched=True, raster_out=True)
                    except:
                        if record == year:
                            print(f'statistics for {var} in {year} not available')
                        if type(record) == list:
                            print(f'statistics for {var} in {year} and month {record[period]} not available')
                        if record == 'day':
                            print(f'statistics for {var} in {year} and day{period+1} not available')
                        continue

                    # Convert the GeoJSON features to a DataFrame
                    features_list = [feature['properties'] for feature in stats]
                    result_df = pd.DataFrame(features_list)

                    # Set csv file name and dir
                    if record == year:
                        csv_dir_name = os.path.join(f'data/csv_data/{var}')
                        csv_file_name = os.path.join(f'data/csv_data/{var}/{year}.csv')
                    if type(record) == list:
                        csv_dir_name = os.path.join(f'data/csv_data/{var}/{year}')
                        csv_file_name = os.path.join(f'data/csv_data/{var}/{year}/{record[period]}.csv')
                    if record == 'day':
                        csv_dir_name = os.path.join(f'data/csv_data/{var}/{year}')
                        csv_file_name = os.path.join(f'data/csv_data/{var}/{year}/day{period+1}.csv')
            
                    # make directory if it doesn't exist
                    Path(csv_dir_name).mkdir(parents=True, exist_ok=True)

                    # save file to csv
                    result_df.to_csv(csv_file_name, index=False)

        #delete raw data files on success
    
    print(f'processed data for silo variable {var} for year {year}')

    return 'success'