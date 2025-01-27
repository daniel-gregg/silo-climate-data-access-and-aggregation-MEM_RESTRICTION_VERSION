# Function to read in the .nc files and convert to tiff with ABS masking

## Set up
import xarray as xr
import os
import numpy as np
import pandas as pd
import glob
import geopandas as gpd
import rasterio as rio 
import rioxarray
import json
import rtree
from rasterio.warp import reproject, Resampling
from rasterio.features import geometry_mask
from rasterstats import zonal_stats
from matplotlib import pyplot as plt 
from shapely.geometry import Point
from rasterio.features import rasterize

def get_zonal_statistics_and_rasters(nc_file_path,abs_sa_data_path):
    masking_shapefile = gpd.read_file(abs_sa_data_path) #this is the 'gpd' var in Yuan's original script
    data_file = xr.open_dataset(nc_file_path) #this is the 'ds_xxx' file in Yuan's original script

    


########## rainfall monthly data zonal stats_ montly tiff file ##########################
# Read the shapefile
gdf = gpd.read_file(sa2_nsw_shp)

# Loop through each year
for year in range(2000, 2011):
    print(year)
    monthly_rain = os.path.join(dir_local, f'{year}.monthly_rain.nc')
    ds_rain = xr.open_dataset(monthly_rain)
    
    ds_rain = ds_rain.reindex(lat=list(reversed(ds_rain.lat)))
    rain_data = ds_rain['monthly_rain']

    ymin = ds_rain.lat.max().values + (0.5 * 0.05)  # Adjust the origin to the upper left
    xmin = ds_rain.lon.min().values - (0.5 * 0.05)
    transform = (0.05, 0, xmin, 0, -0.05, ymin)  # GeoTransform for the TIFF
    meta = {'driver': 'GTiff',
            'dtype': 'float32',
            'transform': transform,
            'width': rain_data.sizes['lon'],
            'height': rain_data.sizes['lat'],
            'count': 1,
            'crs': 4326,
            'nodata': -9999}

    precip_vals = rain_data.values

    # Save each month as a separate GeoTIFF and perform zonal statistics
    for month in range(precip_vals.shape[0]):
        month_idx = month + 1
        save_name_monthly = os.path.join(save_dir, f"{year}_{month_idx:02d}_monthly_rain.tif")
        with rio.open(save_name_monthly, 'w', **meta) as dst:
            dst.write(precip_vals[month, :, :], 1)  # Save each month in a separate file
        
        # Perform zonal statistics on the monthly TIFF
        stats = zonal_stats(gdf, save_name_monthly, stats=['min', 'max', 'mean'], nodata=-9999, geojson_out=True, all_touched=True)
        
        features_list = [feature['properties'] for feature in stats]
        result_df = pd.DataFrame(features_list)
        
        selected_columns = ['SA2_CODE21', 'min', 'max', 'mean']
        result_df = result_df[selected_columns]
        
        output_csv = os.path.join(csv_dir, f"zonal_stats_{year}_{month_idx:02d}_monthly_rain.csv")
        result_df.to_csv(output_csv, index=False)