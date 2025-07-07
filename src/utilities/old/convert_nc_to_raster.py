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
import rasterio as rio 
import calendar

#local imports
from src.utilities.spatial.get_vars_dict_mapping import get_vars_dict_mapping

def convert_nc_to_raster(var, year, data_source, name = ''):

    #check if target tiff files already exist - if so then data is processed   
    data_var_path = here(f'data/silo/{var}/{year}.nc')
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
    tiff_file_name = os.path.join(f'data/tiff_files/{name}/{var}/{year}.tif')
    Path(os.path.join(tiff_file_dir)).mkdir(parents=True, exist_ok=True)

    # set the number of bands for the meta data
    bands = data_vals.shape[0]

    #set metadata
    meta = {'driver': 'GTiff',
            'dtype': 'float32',
            'transform': transform,
            'width': target_data.sizes['lon'],
            'height': target_data.sizes['lat'],
            'count': bands,
            'crs': 4326,
            'nodata': np.nan}
    
    if record == 'year':
        with rio.open(tiff_file_name, 'w', **meta) as dst:
            dst.write(data_vals[0, :, :], 1)  # Save each month in a separate file
    if record == 'month':
            # Select data for the current month
            with rio.open(tiff_file_name, 'w', **meta) as dst:
                for month in range(1, bands+1):
                    monthly_data = target_data.sel(time=target_data['time'].dt.month == month)
                    dst.write(monthly_data.values[0, :, :], month)
    if record == 'day':
        with rio.open(tiff_file_name, 'w', **meta) as dst:
            for day in range(1, bands+1):
                dst.write(data_vals[day-1, :, :], day)

                    