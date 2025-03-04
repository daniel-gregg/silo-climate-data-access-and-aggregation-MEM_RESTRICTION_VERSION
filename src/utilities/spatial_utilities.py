
#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

# web and file utilities
import zipfile
import urllib.request

# Spatial modules/packages
import calendar
import pandas as pd
import numpy as np
import xarray as xr
import rasterio as rio
import geopandas as gpd
from exactextract import exact_extract

#local imports
from src.utilities.data_utilities import get_vars_dict_mapping
from data.user_selected_data_dict import user_selected_data_dict
from src.utilities.aws_boto3.get_silo_boto3_session import get_silo_boto3_session

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

def save_silo_csv(df, var, year, name = None):
    # check if dir exists
    if name:
        target_dir = f'data/csv_data/{name}/{var}'
        if not os.path.exists(target_dir):
            # create path
            Path(target_dir).mkdir(parents=True, exist_ok=True)
        
        # save to target dir
        df.to_csv(f'data/csv_data/{name}/{var}/{year}.csv', index = False)
    else:
        target_dir = f'data/csv_data/{var}'
        if not os.path.exists(target_dir):
            # create path
            Path(target_dir).mkdir(parents=True, exist_ok=True)
        
        # save to target dir
        df.to_csv(f'data/csv_data/{var}/{year}.csv', index = False)

def get_recursive_days_in_year(year, month, days=0):
    if month > 1:
        days = calendar.monthrange(year, month)[1] + days
        return get_recursive_days_in_year(year, month-1, days)
    else:
        days = calendar.monthrange(year, month)[1] + days
        return days
    
def get_month(year, day, month = 1):

    min_days_for_month = get_recursive_days_in_year(year, month)
    if day > min_days_for_month:
        month = month+1
        return get_month(year, day+1, month)
    else:
        return month

### Function to convert netcdf4 files to raster (tiff) files. 
def convert_nc_to_raster(var, year, data_source, name = ''):

    print(f'opening nc data file for {var}-{year} for conversion to raster')
    data_var_path = here(f'data/{data_source}/{var}/{year}.nc')
    data_file = xr.open_dataset(data_var_path) #this is the 'ds_xxx' file in Yuan's original script
    # lat is reversed so reindex
    data_file = data_file.reindex(lat=list(reversed(data_file.lat)))

    # set key values 
    ymin = data_file.lat.max().values + (0.5 * 0.05)  # Adjust the origin to the upper left
    xmin = data_file.lon.min().values - (0.5 * 0.05)
    transform = (0.05, 0, xmin, 0, -0.05, ymin)  # GeoTransform for the TIFF

    # get target varname recorded in the silo data file
    varname_in_file = get_vars_dict_mapping()[data_source][var]

    # get data values and periods
    target_data = data_file[varname_in_file]
    data_vals = target_data.values

    # determine period structure
    if data_vals.shape[0] <=1:
        record = 'year'
    if data_vals.shape[0] <=12:
        record = 'month'
    if data_vals.shape[0]>360 and data_vals.shape[0]<370:
        record = 'day'

    # set tiff file path and make directory if it doesn't exist
    tiff_file_dir = os.path.join(f'data/tiff_files/{name}/{var}')
    Path(os.path.join(tiff_file_dir)).mkdir(parents=True, exist_ok=True)

    # set the number of bands for the meta data
    bands = data_vals.shape[0]
    print(f'{bands} bands found in raster for {var} in {year}')

    #set metadata
    meta = {'driver': 'GTiff',
            'dtype': 'float32',
            'transform': transform,
            'width': target_data.sizes['lon'],
            'height': target_data.sizes['lat'],
            'count': bands,
            'crs': 4326,
            'nodata': np.nan}
    
    tiff_file_name = os.path.join(f'data/tiff_files/{name}/{var}/{year}.tif')

    # year records
    if record == 'year':
        with rio.open(tiff_file_name, 'w', **meta) as dst:
            print(f'writing annual band for {var}-{year} to tiff file')
            dst.write(data_vals[0, :, :], 1)  # Save each month in a separate file
    
    # month records
    if record == 'month':
        # Select data for the current month
        with rio.open(tiff_file_name, 'w', **meta) as dst:
            for month in range(1, bands+1):
                # save tiff band
                print(f'writing monthly band {month} for {var}-{year} to tiff file')
                dst.write(data_vals[month-1, :, :], month)
    
    # daily records
    if record == 'day':
        with rio.open(tiff_file_name, 'w', **meta) as dst:
            for day in range(1, bands+1):
                print(f'writing daily band {day} for {var}-{year} to tiff file')
                dst.write(data_vals[day-1, :, :], day)

    # delete the connection to open up access to file removal etc.
    del dst


### function to import Tiff file (raster), mask it with target shapefile/region, and calculate zonal stats 
# returns a pandas dataframe
def mask_and_merge_var_years_zonal_stats(var, year, name = None, include_cols = []):

    print(f'undertaking zonal stats for {var}-{year}')

    # get data targets
    target_data_dict = user_selected_data_dict()

    # reference masking region statistical area scopes from data dict
    sa_scope = target_data_dict['statistical_areas']

    # masking subsets - check if any specified
    masking_subsets_dict = target_data_dict['masking_subsets']
    
    # initialise an empty df and other things needed
    data_out = pd.DataFrame()
    result_df = pd.DataFrame()
    subsets = [* masking_subsets_dict.keys()]
    
    # first get scope
    for scope in sa_scope:

        for subset in subsets:

            # get the masking shapefile - this includes any subsets
            regions_list = masking_subsets_dict[subset](scope)
            masking_shapefile = get_sa_areas_masking_shapefile(scope, regions_list, name)
            # filter out empty or null geometries
            masking_shapefile = masking_shapefile[~(masking_shapefile['geometry'].is_empty | masking_shapefile['geometry'].isna())]
            # 'explode' the shapefile to remove multipolygons that do not work with exact_extract
            masking_shapefile = masking_shapefile.explode(columns = 'geometry')
            
            # get tiff file
            if name:
                tiff_file_name = f'data/tiff_files/{name}/{var}/{year}.tif'
            else:
                tiff_file_name = f'data/tiff_files/{var}/{year}.tif'

            try:
                
                stats = exact_extract(
                    here(tiff_file_name), 
                    masking_shapefile, 
                    ["mean", "min", "max"], 
                    max_cells_in_memory = 30000000, 
                    strategy = "raster-sequential", 
                    progress = True, 
                    output = 'pandas',
                    include_cols = include_cols)
                
                # collate stats
                # generate new data and rename
                new_data = stats
                rows = new_data.shape[0]
                new_data = pd.concat(
                    [pd.DataFrame({
                        'name' : [name]*rows,
                        'abs_sa_scope' : [scope]*rows,
                        'year' : [year]*rows
                    }),
                    new_data
                    ],
                    axis = 1
                )
                        
                if data_out.empty:
                    # create target df
                    data_out = new_data
                else:
                    #merge onto final df
                    data_out = pd.concat([data_out, new_data], axis = 0)
            
            except:
                print(f'statistics for {var} in {year} not available')
            
            # merge to DF
            if result_df.empty:
                # Initialise df
                result_df = pd.DataFrame(data_out)
            else:
                # Merge df
                result_df = pd.concat([result_df, data_out], axis = 0)
        
        del stats #delete the stats object to remove any residual file connections to the raster 
        
        return result_df

### Final function to operationalise activities related to silo data processing
# saves a csv file with target data for var in year based on masking shapefile
# if var has existing years this data is appended to that. 
def process_silo_var(var, year, name = None):

    # get the tiff file
    convert_nc_to_raster(var, year, data_source = 'silo', name=name)

    # get zonal stats
    df = mask_and_merge_var_years_zonal_stats(var, year, name=name, include_cols=['SA1_CODE21', 'AREASQKM21'])
    
    # check if data file for var exists already
    if name:
        file_path = f'data/csv_data/{name}/{var}/{year}.csv'
    else: 
        file_path = f'data/csv_data/{var}/{year}.csv'

    # save back to file
    save_silo_csv(df, var, year, name)


def get_sa_areas_masking_shapefile(scope, regions_list = None, name = None):
    
    #get base shapefile
    abs_region_path = here(f'data/SA_data_shapefiles/{scope}')
    base_shapefile = gpd.read_file(abs_region_path)

    sa_code_var_dict = {
        'sa1' : 'SA1_CODE21',
        'sa2' : 'SA2_CODE21',
        'sa3' : 'SA3_CODE21',
        'sa4' : 'SA4_CODE21',
    }

    # subset based on regions
    if regions_list:

        # regions_list will include a set of sa codes based on the sa scope
        codes_in_shapefile = base_shapefile[sa_code_var_dict[scope]]

        # first subset removing strings that are not convertable to integers (i.e. 'zzzzz')
        def value_error_check(x):
            try:
                int(x)
                return x
            except:
                pass
        codes_in_shapefile = [value_error_check(x) for x in codes_in_shapefile]
        codes_in_shapefile = [x for x in codes_in_shapefile if x is not None]
        
        # create new subset of sa codes by checking for which are in regions_list
        codes_in_shapefile = [x for x in codes_in_shapefile if int(x) in regions_list]
        
        # subset the base_shapefile to the target regions
        mask = base_shapefile[sa_code_var_dict[scope]].isin(codes_in_shapefile)
        new_shapefile = base_shapefile[mask]
    
    return new_shapefile   

def get_silo_data(var, year):

    # create session
    s3_session = get_silo_boto3_session()
    bucket = 'silo-open-data'

    # check data and return dict for accessing boto3 data
    silo_vars_all = get_vars_dict_mapping()['silo'] #mapping for all available silo vars from varnames to boto3 filenames (not including prefix and year/month/day)
    
    target_subdir = here(f'data/silo/{var}')
    if not os.path.isdir(target_subdir):
        #create directory
        Path(target_subdir).mkdir(parents=True, exist_ok=True)

        #check csv - if present that var/year is already processed
    file_target = f'Official/annual/{silo_vars_all[var]}/{year}.{silo_vars_all[var]}.nc'
    target_save_path = os.path.join(target_subdir, f'{year}.nc')

    # also check for the target file existence itself
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
        print(f'silo data for {var} for {year} already exists in your directory - continuing to next')