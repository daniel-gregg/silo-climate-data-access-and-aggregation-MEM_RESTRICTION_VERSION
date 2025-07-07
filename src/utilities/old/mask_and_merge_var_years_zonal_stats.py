
#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

## Spatial modules/packages
import pandas as pd
import numpy as np
from rasterstats import zonal_stats
import rasterio
import calendar 
import rioxarray

from src.utilities.spatial.get_sa_areas_masking_shapefile import get_sa_areas_masking_shapefile
from data.user_selected_data_dict import user_selected_data_dict

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

def mask_and_merge_var_years_zonal_stats(var, year, name=None):

    # get data targets
    target_data_dict = user_selected_data_dict()

    # reference masking region statistical area scopes from data dict
    sa_scope = target_data_dict['statistical_areas']

    # masking subsets - check if any specified
    masking_subsets_dict = target_data_dict['masking_subsets']
    
    # initialise an empty df and other things needed
    data_out = pd.DataFrame()
    subsets = [* masking_subsets_dict.keys()]
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    
    # first get scope
    for scope in sa_scope:

        # check if there is a masking function specified
        if masking_subsets_dict:
            for subset in subsets:
                # get the masking shapefile - this includes any subsets
                regions_list = masking_subsets_dict[subset](scope)
                masking_shapefile = get_sa_areas_masking_shapefile(scope, regions_list, name)
                # filter out empty or null geometries
                masking_shapefile = masking_shapefile[~(masking_shapefile['geometry'].is_empty | masking_shapefile['geometry'].isna())]

                if name:
                    tiff_file_name = f'data/tiff_files/{name}/{var}/{year}.tif'
                else:
                    tiff_file_name = f'data/tiff_files/{var}/{year}.tif'
                # Perform zonal statistics on the monthly TIFF

                # Earlier test of pre-clipping raster to speed up does not result in a speed improvement    
                #geometries = masking_shapefile['geometry']
                #clipped = rioxarray.open_rasterio(tiff_file_name, masked=True).rio.clip(geometries)
                #clipped.rio.to_raster(f'data/tiff_files/{name}/{var}/{year}_clipped.tif', compress='LZMA', tiled=True)
                
                try:
                    #load file
                    with rasterio.open(tiff_file_name) as src:
                        bands = src.count # number of bands in file - reflects whether monthly or daily data
                
                    if bands == 1:
                        ### YEARLY RECORDS ###
                        stats = zonal_stats(masking_shapefile, tiff_file_name, geojson_out=True, nodata=np.nan, stats=['mean', 'min', 'max'])
                        features_list = [feature['properties'] for feature in stats]
                        
                        # generate new data
                        new_data = pd.DataFrame(features_list)
                        new_data['name'] = name
                        new_data['abs_sa_scope'] = scope
                        new_data['year'] = year
                        new_data['month'] = np.nan
                        new_data['day'] = np.nan

                        if data_out.empty:
                            # create target df
                            data_out = new_data
                        else:
                            #merge onto final df
                            data_out = pd.concat([data_out, new_data])

                    if bands == 12:
                        ### MONTHLY RECORDS ###
                        for band in range(bands):
                            stats = zonal_stats(masking_shapefile, tiff_file_name, geojson_out=True, nodata=-9999, stats=['mean', 'min', 'max'], band_num = band)
                            features_list = [feature['properties'] for feature in stats]
                            
                            # generate new data
                            new_data = pd.DataFrame(features_list)
                            new_data['name'] = name
                            new_data['abs_sa_scope'] = scope
                            new_data['year'] = year
                            new_data['month'] = months[band-1]
                            new_data['day'] = np.nan

                        if data_out.empty:
                            # create target df
                            data_out = new_data
                        else:
                            #merge onto final df
                            data_out = pd.concat([data_out, new_data])
                    
                    else:
                        ### DAILY RECORDS ###
                        if bands > 366 or bands < 365:
                            Warning(f'bands must be either year, months or days ref: {var} in {year} has {bands} bands')
                        
                        ## Initialise items for indexing months
                        month_base = 1 #set initial month base for aggregation

                        # loop through bands (day records) and save to df
                        for band in range(bands):
                            #get current month first
                            current_month_index = get_month(year, band)

                            #get day number in month
                            if current_month_index == 1:
                                day_in_month = band + 1
                            else:
                                day_in_month = band + 1 - get_recursive_days_in_year(year, current_month_index - 1)
                            
                            # get zonal stats for day
                            stats = zonal_stats(masking_shapefile, tiff_file_name, geojson_out=True, nodata=np.nan, stats=['mean', 'min', 'max'], band_num = band)
                            features_list = [feature['properties'] for feature in stats]
                            
                            # generate new_data
                            new_data = pd.DataFrame(features_list) 
                            new_data['name'] = name
                            new_data['abs_sa_scope'] = scope
                            new_data['year'] = year
                            new_data['month'] = months[current_month_index-1]
                            new_data['day'] = day_in_month
                            
                            if data_out.empty:
                                # create subdat dataframe
                                data_out = new_data
                            else:
                                # merge onto data_out
                                data_out = pd.concat([data_out, new_data])

                            # check if need to update month index    
                            if current_month_index == month_base:
                                # set updated month base for next base
                                month_base += 1
                    
                except:
                    print(f'statistics for {var} in {year} not available')

                # Convert the GeoJSON features to a DataFrame
                

                # merge to DF
                if not result_df:
                    # Initialise df
                    result_df = pd.DataFrame(data_out)
                else:
                    # Merge df
                    result_df = pd.concat([result_df, data_out], axis = 0)
        
        return result_df
