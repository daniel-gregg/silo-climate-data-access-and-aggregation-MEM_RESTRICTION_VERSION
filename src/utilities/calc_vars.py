## functions to calculate final target variables at a monthly timestep


#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

import calendar
import pandas as pd
import numpy as np

### Functions

# utility function to return number of days up to a given month in a given year
def get_recursive_days_in_year(year, month, days=0):
    if month > 1:
        days = calendar.monthrange(year, month)[1] + days
        return get_recursive_days_in_year(year, month-1, days)
    else:
        days = calendar.monthrange(year, month)[1] + days
        return days

# utility function to return the current month for a given year for a given day
def get_month(year, day_, month = 1):

    min_days_for_month = get_recursive_days_in_year(year, month)
    if day_ > min_days_for_month:
        if not month == 12:
            month = month+1
            return get_month(year, day_, month)
        else:
            return month
    else:
        return month

def get_data(var, year, name = None):
    if name:
        file_path = f'data/csv_data/{name}/{var}/{year}.csv'
    else:
        file_path = f'data/csv_data/{var}/{year}.csv'

    try:
        data = pd.read_csv(here(file_path))
    except:
        Warning(f'File at {file_path} not found')
        data = []

    return data

def get_perplexity(dat):
    # dat should be a list representing the share/probability of a temporal range of observations for a single variable
    # (e.g. a month of the proportion of total monthly rainfall observed on each day of the month)
    transform = 0
    for x in dat:
        if x == 0:
            continue
        else:
            transform += x * np.log2(x)
    
    # negative sum to get final value
    perplexity = 2**-transform
    expected_bits_in_series = len(dat)
    intensity = (1 - (perplexity / expected_bits_in_series))/(1-(1/len(dat)))

    # scale intensity so that it is 0-1 based on maximum range limit of 1 - 1/len(x)

    return {'perplexity' : perplexity, 'intensity' : intensity}

def get_rainfall_vars(name = None):
    ### Rainfall intensity
    # unitless - a measure of dispersion (across time) of given rainfall. This ensures low correlation with rainfall volume variables
    
    # get dirpath and print listdir
    if name:
        dirpath = f'data/csv_data/{name}/daily_rainfall'
    else:
        dirpath = f'data/csv_data/daily_rainfall'

    years = os.listdir(here(dirpath))
    years = [int(year.split(".")[0]) for year in years]
    print(f'years {years} present for daily rainfall - processing to collate monthly means and monthly intensity indices')

    for year in years:
        print(f'initiating processing of daily rainfall for {year}')

        data = get_data('daily_rainfall', year, name = name)

        ids_list = [*set(data['SA1_CODE21'])] # list of SA1 code ids for each SA1 region

        #data is in a wide format with column names as 'band_1_mean', 'band_2_mean' etc up to the number of days in the year
        vars = data.columns

        # remove non-data columns including area and collate only mean vars
        vars = [var for var in vars if 'band' in var]
        vars = [var for var in vars if 'mean' in var]

        # get days in year
        if calendar.isleap(2001):
            days_in_year = 366
        else:
            days_in_year = 365

        # initialise empty df:
        out_data_rainfall = pd.DataFrame()
        out_data_intensity = pd.DataFrame()

        # get daily intensity of rainfall first
        for id in ids_list:
            subdat = data.loc[data['SA1_CODE21']==id, vars]
            
            # need to account for possible multiple observations for multi-polygon SA1 areas.
            # these have the same mean values so just need to take the top one, but take mean as a precautionary measure. 
            if subdat.shape[0]>1:
                subdat = pd.DataFrame(subdat.mean(axis=0)).T
            
            # get/initialise rainfall totals for sa1 region
            total_annual_rainfall = np.sum(subdat[vars],axis = 1).item()
            total_proportion_rainfall_by_day = [subdat[x].item()/total_annual_rainfall for x in subdat.columns]
            total_rainfall_by_month = []
            monthly_rainfall = []
            monthly_intensity = []
            monthly_proportion_rainfall = []

            for day in range(days_in_year):
                month = get_month(year, day+1)
                if month == 1:
                    rain_to_last_month = 0
                else:
                    days_to_last_month = get_recursive_days_in_year(year, get_month(year, day+1)-1)
                    rain_to_last_month = np.sum(subdat.iloc[: , [i for i in range(days_to_last_month)]], axis = 1).item()

                year_days_to_end_of_this_month = get_recursive_days_in_year(year, get_month(year, day+1))
                day_rain = subdat.iloc[:, day].item()
                monthly_rainfall.append(day_rain)
                
                # check if last day of month - if so add entry to total_monthly_rainfall
                if day+1 == year_days_to_end_of_this_month:
                    monthly_total = np.sum(monthly_rainfall).item()
                    total_rainfall_by_month.append(monthly_total)
                    if sum(monthly_rainfall) == 0:
                        monthly_intensity.append(0)
                    else:
                        monthly_proportion_rainfall = [x / monthly_total for x in monthly_rainfall]
                        # get intensity measure for each month
                        monthly_intensity.append(get_perplexity(monthly_proportion_rainfall)['intensity'].item())

                    # finally reset monthly_rainfall
                    monthly_rainfall = []
                
            new_data_rainfall = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual_rainfall_mm' : [total_annual_rainfall],
                'january_rainfall_mm' : [total_rainfall_by_month[0]],
                'february_rainfall_mm' : [total_rainfall_by_month[1]],
                'march_rainfall_mm' : [total_rainfall_by_month[2]],
                'april_rainfall_mm' : [total_rainfall_by_month[3]],
                'may_rainfall_mm' : [total_rainfall_by_month[4]],
                'june_rainfall_mm' : [total_rainfall_by_month[5]],
                'july_rainfall_mm' : [total_rainfall_by_month[6]],
                'august_rainfall_mm' : [total_rainfall_by_month[7]],
                'september_rainfall_mm' : [total_rainfall_by_month[8]],
                'october_rainfall_mm' : [total_rainfall_by_month[9]],
                'november_rainfall_mm' : [total_rainfall_by_month[10]],
                'december_rainfall_mm' : [total_rainfall_by_month[11]]
            })

            new_data_intensity = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [get_perplexity(total_proportion_rainfall_by_day)['intensity']],
                'january' : [monthly_intensity[0]],
                'february' : [monthly_intensity[1]],
                'march' : [monthly_intensity[2]],
                'april' : [monthly_intensity[3]],
                'may' : [monthly_intensity[4]],
                'june' : [monthly_intensity[5]],
                'july' : [monthly_intensity[6]],
                'august' : [monthly_intensity[7]],
                'september' : [monthly_intensity[8]],
                'october' : [monthly_intensity[9]],
                'november' : [monthly_intensity[10]],
                'december' : [monthly_intensity[11]]
            })

            if out_data_rainfall.empty:
                # create the out dataframe
                out_data_rainfall = new_data_rainfall
            else:
                out_data_rainfall = pd.concat([
                    out_data_rainfall,
                    new_data_rainfall
                    ],
                    axis = 0
                )

            if out_data_intensity.empty:
                # create the out dataframe
                out_data_intensity = new_data_intensity
            else:
                out_data_intensity = pd.concat([
                    out_data_intensity,
                    new_data_intensity
                    ],
                    axis = 0
                )

    # save output csv with id as single row
    out_data_rainfall.to_csv(here(f'data/csv_data/{name}/final_data/rainfall_mm.csv'))
    out_data_intensity.to_csv(here(f'data/csv_data/{name}/final_data/rainfall_intensity.csv'))


def get_var_means_as_monthly_records(var, name=None):
    ## set dirpath

    if name:
        dirpath = f'data/csv_data/{name}/{var}'
    else:
        dirpath = f'data/csv_data/{var}'
    
    years = os.listdir(here(dirpath))
    years = [int(year.split(".")[0]) for year in years]
    print(f'years {years} present for {var} - processing to collate monthly means')

    for year in years:
        print(f'initiating processing of {var} for {year}')

        if name:
            data = pd.read_csv(f'data/csv_data/{name}/{var}/{year}.csv')
        else:
            data = pd.read_csv(f'data/csv_data/{var}/{year}.csv')

        ids_list = [*set(data['SA1_CODE21'])] # list of SA1 code ids for each SA1 region

        #data is in a wide format with column names as 'band_1_mean', 'band_2_mean' etc up to the number of days in the year
        vars = data.columns

        # remove non-data columns including area and collate only mean vars
        vars = [var for var in vars if 'band' in var]
        vars = [var for var in vars if 'mean' in var]

        # get days in year
        if calendar.isleap(2001):
            days_in_year = 366
        else:
            days_in_year = 365

        # initialise empty df:
        out_data = pd.DataFrame()

        # get daily intensity of rainfall first
        for id in ids_list:
            subdat = data.loc[data['SA1_CODE21']==id, vars]
            
            # need to account for possible multiple observations for multi-polygon SA1 areas.
            # these have the same mean values so just need to take the top one, but take mean as a precautionary measure. 
            if subdat.shape[0]>1:
                subdat = pd.DataFrame(subdat.mean(axis=0)).T
                area_ha = np.nanmean(data.loc[data['SA1_CODE21']==id,'AREASQKM21']).item() * 100,
            else:
                area_ha = data.loc[data['SA1_CODE21']==id,'AREASQKM21'].item() * 100,
            
            # get/initialise rainfall totals for sa1 region
            total_annual_value = np.nanmean(subdat[vars],axis = 1).item()
            total_values_by_month = []
            monthly_values = []

            for day in range(days_in_year):
                year_days_to_end_of_this_month = get_recursive_days_in_year(year, get_month(year, day+1))
                day_value = subdat.iloc[:, day].item()
                monthly_values.append(day_value)
                
                # check if last day of month - if so add entry to total_monthly_rainfall
                if day+1 == year_days_to_end_of_this_month:
                    total_values_by_month.append(np.nanmean(monthly_values).item())

                    # finally reset monthly_rainfall
                    monthly_values = []
                
            new_data = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'area_ha' : [area_ha],
                f'annual' : [total_annual_value],
                f'january' : [total_values_by_month[0]],
                f'february' : [total_values_by_month[1]],
                f'march' : [total_values_by_month[2]],
                f'april' : [total_values_by_month[3]],
                f'may' : [total_values_by_month[4]],
                f'june' : [total_values_by_month[5]],
                f'july' : [total_values_by_month[6]],
                f'august' : [total_values_by_month[7]],
                f'september' : [total_values_by_month[8]],
                f'october' : [total_values_by_month[9]],
                f'november' : [total_values_by_month[10]],
                f'december' : [total_values_by_month[11]]
            })

            if out_data.empty:
                # create the out dataframe
                out_data = new_data
            else:
                out_data = pd.concat([
                    out_data,
                    new_data
                    ],
                    axis = 0
                )

        # save output csv with id as single row
    out_data.to_csv(here(f'data/csv_data/{name}/final_data/{var}_mean.csv'))

## get hot days per month
def get_hot_days_per_month(name = None):
    ## uses max_temp csv data to get hot days per month
    # hot days defined as maximum above 40 degrees celcius
    # very hot days defined as maximum above 45 degrees celcius
    # hot nights defined as minimum above 25 degrees celcius (moved to 'get_cold_days_per_month')
    # potential frost days defined as minimum below 1 degree celcius (moved to 'get_cold_days_per_month')

    # get dirpath and print listdir
    if name:
        dirpath = f'data/csv_data/{name}/max_temp'
    else:
        dirpath = f'data/csv_data/max_temp'

    years = os.listdir(here(dirpath))
    years = [int(year.split(".")[0]) for year in years]
    print(f'years {years} present for max_temp - processing to collate monthly means and monthly intensity indices')

    for year in years:
        print(f'initiating processing of max_temp for {year}')

        if name:
            data = pd.read_csv(f'data/csv_data/{name}/max_temp/{year}.csv')
        else:
            data = pd.read_csv(f'data/csv_data/max_temp/{year}.csv')

        ids_list = [*set(data['SA1_CODE21'])] # list of SA1 code ids for each SA1 region

        #data is in a wide format with column names as 'band_1_mean', 'band_2_mean' etc up to the number of days in the year
        vars = data.columns

        # remove non-data columns including area and collate only mean vars
        vars = [var for var in vars if 'band' in var]
        vars = [var for var in vars if 'mean' in var]

        # get days in year
        if calendar.isleap(2001):
            days_in_year = 366
        else:
            days_in_year = 365

        # initialise empty df:
        out_data_hot = pd.DataFrame()
        out_data_very_hot = pd.DataFrame()

        # get daily intensity of rainfall first
        for id in ids_list:
            subdat = data.loc[data['SA1_CODE21']==id, vars]
            
            # need to account for possible multiple observations for multi-polygon SA1 areas.
            # these have the same mean values so just need to take the top one, but take mean as a precautionary measure. 
            if subdat.shape[0]>1:
                subdat = pd.DataFrame(subdat.mean(axis=0)).T
            
            # get/initialise rainfall totals for sa1 region
            annual_vals = [subdat[x].item for x in subdat.columns]
            annual_hot_days = len([x for x in annual_vals if x > 40]).item()
            annual_very_hot_days = len([x for x in annual_vals if x > 45]).item()
            monthly_values = []
            hot_days_by_month = []
            very_hot_days_by_month = []
            
            for day in range(days_in_year):
                year_days_to_end_of_this_month = get_recursive_days_in_year(year, get_month(year, day+1))
                day_values = subdat.iloc[:, day].item()
                monthly_values.append(day_values)
                
                # check if last day of month - if so add entries to 'hot_days_by_month' and 'very_hot_days_by_month'
                if day+1 == year_days_to_end_of_this_month:
                    hot_days_by_month.append(len([x for x in day_values if x > 40]))
                    very_hot_days_by_month.append(len([x for x in day_values if x > 45]))

                    # finally reset monthly_rainfall
                    monthly_values = []
                
            new_data_hot = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [annual_hot_days],
                'january' : [hot_days_by_month[0]],
                'february' : [hot_days_by_month[1]],
                'march' : [hot_days_by_month[2]],
                'april' : [hot_days_by_month[3]],
                'may' : [hot_days_by_month[4]],
                'june' : [hot_days_by_month[5]],
                'july' : [hot_days_by_month[6]],
                'august' : [hot_days_by_month[7]],
                'september' : [hot_days_by_month[8]],
                'october' : [hot_days_by_month[9]],
                'november' : [hot_days_by_month[10]],
                'december' : [hot_days_by_month[11]]
            })

            new_data_very_hot = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [annual_very_hot_days],
                'january' : [very_hot_days_by_month[0]],
                'february' : [very_hot_days_by_month[1]],
                'march' : [very_hot_days_by_month[2]],
                'april' : [very_hot_days_by_month[3]],
                'may' : [very_hot_days_by_month[4]],
                'june' : [very_hot_days_by_month[5]],
                'july' : [very_hot_days_by_month[6]],
                'august' : [very_hot_days_by_month[7]],
                'september' : [very_hot_days_by_month[8]],
                'october' : [very_hot_days_by_month[9]],
                'november' : [very_hot_days_by_month[10]],
                'december' : [very_hot_days_by_month[11]]
            })

            if out_data_hot.empty:
                # create the out dataframe
                out_data_hot = new_data_hot
            else:
                out_data_hot = pd.concat([
                    out_data_hot,
                    new_data_hot
                    ],
                    axis = 0
                )

            
            if out_data_very_hot.empty:
                # create the out dataframe
                out_data_very_hot = new_data_very_hot
            else:
                out_data_very_hot = pd.concat([
                    out_data_very_hot,
                    new_data_very_hot
                    ],
                    axis = 0
                )

    # save output csv with id as single row
    out_data_hot.to_csv(here(f'data/csv_data/{name}/final_data/hot_days.csv'))
    out_data_very_hot.to_csv(here(f'data/csv_data/{name}/final_data/very_hot_days.csv'))

## get cold days per month
def get_cold_days_per_month(name = None):
    ## uses min_temp csv data to get hot nights and possible frost days per month
    # hot nights defined as minimum above 25 degrees celcius 
    # potential frost days defined as minimum below 1 degree celcius 

    # get dirpath and print listdir
    if name:
        dirpath = f'data/csv_data/{name}/min_temp'
    else:
        dirpath = f'data/csv_data/min_temp'

    years = os.listdir(here(dirpath))
    years = [int(year.split(".")[0]) for year in years]
    print(f'years {years} present for min_temp - processing to collate monthly means and monthly intensity indices')

    for year in years:
        print(f'initiating processing of min_temp for {year}')

        if name:
            data = pd.read_csv(f'data/csv_data/{name}/min_temp/{year}.csv')
        else:
            data = pd.read_csv(f'data/csv_data/min_temp/{year}.csv')

        ids_list = [*set(data['SA1_CODE21'])] # list of SA1 code ids for each SA1 region

        #data is in a wide format with column names as 'band_1_mean', 'band_2_mean' etc up to the number of days in the year
        vars = data.columns

        # remove non-data columns including area and collate only mean vars
        vars = [var for var in vars if 'band' in var]
        vars = [var for var in vars if 'mean' in var]

        # get days in year
        if calendar.isleap(2001):
            days_in_year = 366
        else:
            days_in_year = 365

        # initialise empty df:
        out_data_hot_nights = pd.DataFrame()
        out_data_frost = pd.DataFrame()

        # get daily intensity of rainfall first
        for id in ids_list:
            subdat = data.loc[data['SA1_CODE21']==id, vars]
            
            # need to account for possible multiple observations for multi-polygon SA1 areas.
            # these have the same mean values so just need to take the top one, but take mean as a precautionary measure. 
            if subdat.shape[0]>1:
                subdat = pd.DataFrame(subdat.mean(axis=0)).T
            
            # get/initialise rainfall totals for sa1 region
            annual_vals = [subdat[x].item for x in subdat.columns]
            annual_hot_nights = len([x for x in annual_vals if x > 25]).item()
            annual_frost_days = len([x for x in annual_vals if x < 1]).item()
            monthly_values = []
            hot_nights_by_month = []
            frost_days_by_month = []
            
            for day in range(days_in_year):
                year_days_to_end_of_this_month = get_recursive_days_in_year(year, get_month(year, day+1))
                day_values = subdat.iloc[:, day].item()
                monthly_values.append(day_values)
                
                # check if last day of month - if so add entries to 'hot_days_by_month' and 'very_hot_days_by_month'
                if day+1 == year_days_to_end_of_this_month:
                    hot_nights_by_month.append(len([x for x in day_values if x > 25]))
                    frost_days_by_month.append(len([x for x in day_values if x < 1]))

                    # finally reset monthly_rainfall
                    monthly_values = []
                
            new_data_hot_nights = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [annual_hot_nights],
                'january' : [hot_nights_by_month[0]],
                'february' : [hot_nights_by_month[1]],
                'march' : [hot_nights_by_month[2]],
                'april' : [hot_nights_by_month[3]],
                'may' : [hot_nights_by_month[4]],
                'june' : [hot_nights_by_month[5]],
                'july' : [hot_nights_by_month[6]],
                'august' : [hot_nights_by_month[7]],
                'september' : [hot_nights_by_month[8]],
                'october' : [hot_nights_by_month[9]],
                'november' : [hot_nights_by_month[10]],
                'december' : [hot_nights_by_month[11]]
            })

            new_data_frost = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [annual_frost_days],
                'january' : [frost_days_by_month[0]],
                'february' : [frost_days_by_month[1]],
                'march' : [frost_days_by_month[2]],
                'april' : [frost_days_by_month[3]],
                'may' : [frost_days_by_month[4]],
                'june' : [frost_days_by_month[5]],
                'july' : [frost_days_by_month[6]],
                'august' : [frost_days_by_month[7]],
                'september' : [frost_days_by_month[8]],
                'october' : [frost_days_by_month[9]],
                'november' : [frost_days_by_month[10]],
                'december' : [frost_days_by_month[11]]
            })

            if out_data_hot_nights.empty:
                # create the out dataframe
                out_data_hot = new_data_hot_nights
            else:
                out_data_hot_nights = pd.concat([
                    out_data_hot_nights,
                    new_data_hot_nights
                    ],
                    axis = 0
                )

            
            if out_data_frost.empty:
                # create the out dataframe
                out_data_frost = new_data_frost
            else:
                out_data_frost = pd.concat([
                    out_data_frost,
                    new_data_frost
                    ],
                    axis = 0
                )

    # save output csv with id as single row
    out_data_hot_nights.to_csv(here(f'data/csv_data/{name}/final_data/hot_nights.csv'))
    out_data_frost.to_csv(here(f'data/csv_data/{name}/final_data/frost_days.csv'))

def get_average_monthly_temps(name=None):
    ## uses min_temp csv data to get hot nights and possible frost days per month
    # hot nights defined as minimum above 25 degrees celcius 
    # potential frost days defined as minimum below 1 degree celcius 

    # get dirpath and print listdir
    if name:
        dirpath_max = f'data/csv_data/{name}/max_temp'
        dirpath_min = f'data/csv_data/{name}/min_temp'
    else:
        dirpath_max = f'data/csv_data/max_temp'
        dirpath_min = f'data/csv_data/min_temp'

    years_max = os.listdir(here(dirpath_max))
    years_min = os.listdir(here(dirpath_min))

    years_max = [int(year.split(".")[0]) for year in years_max]
    years_min = [int(year.split(".")[0]) for year in years_min]

    if not years_max == years_min:
        ValueError('Years of data are not the same for max_temp and min_temp. Please remedy before continuing')

    print(f'years {years_max} present for min_temp - processing to collate monthly means and monthly intensity indices')

    for year in years_max:
        print(f'initiating processing of average temperatures for {year}')

        if name:
            data_min = pd.read_csv(f'data/csv_data/{name}/min_temp/{year}.csv')
            data_max = pd.read_csv(f'data/csv_data/{name}/max_temp/{year}.csv')
        else:
            data_min = pd.read_csv(f'data/csv_data/min_temp/{year}.csv')
            data_max = pd.read_csv(f'data/csv_data/max_temp/{year}.csv')

        ids_list_min = [*set(data_min['SA1_CODE21'])] # list of SA1 code ids for each SA1 region
        ids_list_max = [*set(data_max['SA1_CODE21'])] # list of SA1 code ids for each SA1 region

        #data is in a wide format with column names as 'band_1_mean', 'band_2_mean' etc up to the number of days in the year
        vars_min = data_min.columns
        vars_max = data_max.columns

        # remove non-data columns including area and collate only mean vars
        vars_min = [var for var in vars_min if 'band' in var]
        vars_min = [var for var in vars_min if 'mean' in var]
        vars_max = [var for var in vars_max if 'band' in var]
        vars_max = [var for var in vars_max if 'mean' in var]

        # get days in year
        if calendar.isleap(2001):
            days_in_year = 366
        else:
            days_in_year = 365

        # initialise empty df:
        out_data = pd.DataFrame()

        # get daily intensity of rainfall first
        for id in ids_list_max:
            subdat_min = data_min.loc[data_min['SA1_CODE21']==id, vars]
            subdat_max = data_max.loc[data_max['SA1_CODE21']==id, vars]
            
            if not subdat_min.shape[0] == subdat_max.shape[0]:
                ValueError(f'ID {id} present in max_temp is missing from min_temp')

            # need to account for possible multiple observations for multi-polygon SA1 areas.
            # these have the same mean values so just need to take the top one, but take mean as a precautionary measure. 
            if subdat_min.shape[0]>1:
                subdat_min = pd.DataFrame(subdat_min.mean(axis=0)).T
                subdat_max = pd.DataFrame(subdat_max.mean(axis=0)).T
            
            # get/initialise rainfall totals for sa1 region
            # zip min and max together first
            average_temps = [np.mean(x) for x in zip(subdat_min, subdat_max)] # returns mean for each period (day) of min and max temp
            annual_vals = [x.item for x in average_temps]
            avg_annual_temp = np.mean(annual_vals).item()
            avg_temp_by_month = []
            monthly_values = []
            
            for day in range(days_in_year):
                year_days_to_end_of_this_month = get_recursive_days_in_year(year, get_month(year, day+1))
                monthly_values.append(annual_vals[day])
                
                # check if last day of month - if so add entries to 'hot_days_by_month' and 'very_hot_days_by_month'
                if day+1 == year_days_to_end_of_this_month:
                    avg_temp_by_month.append(np.mean(monthly_values))

                    # finally reset monthly_rainfall
                    monthly_values = []
                
            new_data = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [avg_annual_temp],
                'january' : [avg_temp_by_month[0]],
                'february' : [avg_temp_by_month[1]],
                'march' : [avg_temp_by_month[2]],
                'april' : [avg_temp_by_month[3]],
                'may' : [avg_temp_by_month[4]],
                'june' : [avg_temp_by_month[5]],
                'july' : [avg_temp_by_month[6]],
                'august' : [avg_temp_by_month[7]],
                'september' : [avg_temp_by_month[8]],
                'october' : [avg_temp_by_month[9]],
                'november' : [avg_temp_by_month[10]],
                'december' : [avg_temp_by_month[11]]
            })

            if out_data.empty:
                # create the out dataframe
                out_data = new_data
            else:
                out_data = pd.concat([
                    out_data,
                    new_data
                    ],
                    axis = 0
                )

    # save output csv with id as single row
    out_data.to_csv(here(f'data/csv_data/{name}/final_data/avg_temperature.csv'))


def get_high_and_extreme_vpd_days_per_month(data, year, name = None):
    ## uses vapour_pressure_deficit csv data to get high and extreme vpd days per mont
    # high vpd defined as vpd > 0.8
    # extreme vpd defined as vpd > 1

    # get dirpath and print listdir
    if name:
        dirpath = f'data/csv_data/{name}/vapour_pressure_deficit'
    else:
        dirpath = f'data/csv_data/vapour_pressure_deficit'

    years = os.listdir(here(dirpath))
    years = [int(year.split(".")[0]) for year in years]
    print(f'years {years} present for vapour_pressure_deficit - processing to collate monthly means and monthly intensity indices')

    for year in years:
        print(f'initiating processing of vapour_pressure_deficit for {year}')

        if name:
            data = pd.read_csv(f'data/csv_data/{name}/vapour_pressure_deficit/{year}.csv')
        else:
            data = pd.read_csv(f'data/csv_data/vapour_pressure_deficit/{year}.csv')

        ids_list = [*set(data['SA1_CODE21'])] # list of SA1 code ids for each SA1 region

        #data is in a wide format with column names as 'band_1_mean', 'band_2_mean' etc up to the number of days in the year
        vars = data.columns

        # remove non-data columns including area and collate only mean vars
        vars = [var for var in vars if 'band' in var]
        vars = [var for var in vars if 'mean' in var]

        # get days in year
        if calendar.isleap(2001):
            days_in_year = 366
        else:
            days_in_year = 365

        # initialise empty df:
        out_data_high_vpd = pd.DataFrame()
        out_data_extreme_vpd = pd.DataFrame()

        # get daily intensity of rainfall first
        for id in ids_list:
            subdat = data.loc[data['SA1_CODE21']==id, vars]
            
            # need to account for possible multiple observations for multi-polygon SA1 areas.
            # these have the same mean values so just need to take the top one, but take mean as a precautionary measure. 
            if subdat.shape[0]>1:
                subdat = pd.DataFrame(subdat.mean(axis=0)).T
            
            # get/initialise rainfall totals for sa1 region
            annual_vals = [subdat[x].item for x in subdat.columns]
            annual_high_vpd = len([x for x in annual_vals if x > 25]).item()
            annual_extreme_vpd = len([x for x in annual_vals if x < 1]).item()
            monthly_values = []
            high_vpd_by_month = []
            extreme_vpd_by_month = []

            for day in range(days_in_year):
                year_days_to_end_of_this_month = get_recursive_days_in_year(year, get_month(year, day+1))
                day_values = subdat.iloc[:, day].item()
                monthly_values.append(day_values)
                
                # check if last day of month - if so add entries to 'hot_days_by_month' and 'very_hot_days_by_month'
                if day+1 == year_days_to_end_of_this_month:
                    high_vpd_by_month.append(len([x for x in day_values if x > 25]))
                    extreme_vpd_by_month.append(len([x for x in day_values if x < 1]))

                    # finally reset monthly_rainfall
                    monthly_values = []
                
            new_data_high_vpd = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [annual_high_vpd],
                'january' : [high_vpd_by_month[0]],
                'february' : [high_vpd_by_month[1]],
                'march' : [high_vpd_by_month[2]],
                'april' : [high_vpd_by_month[3]],
                'may' : [high_vpd_by_month[4]],
                'june' : [high_vpd_by_month[5]],
                'july' : [high_vpd_by_month[6]],
                'august' : [high_vpd_by_month[7]],
                'september' : [high_vpd_by_month[8]],
                'october' : [high_vpd_by_month[9]],
                'november' : [high_vpd_by_month[10]],
                'december' : [high_vpd_by_month[11]]
            })

            new_data_extreme_vpd = pd.DataFrame({
                'id': [id],
                'year' : [year],
                'annual' : [annual_extreme_vpd],
                'january' : [extreme_vpd_by_month[0]],
                'february' : [extreme_vpd_by_month[1]],
                'march' : [extreme_vpd_by_month[2]],
                'april' : [extreme_vpd_by_month[3]],
                'may' : [extreme_vpd_by_month[4]],
                'june' : [extreme_vpd_by_month[5]],
                'july' : [extreme_vpd_by_month[6]],
                'august' : [extreme_vpd_by_month[7]],
                'september' : [extreme_vpd_by_month[8]],
                'october' : [extreme_vpd_by_month[9]],
                'november' : [extreme_vpd_by_month[10]],
                'december' : [extreme_vpd_by_month[11]]
            })

            if out_data_high_vpd.empty:
                # create the out dataframe
                out_data_high_vpd = new_data_high_vpd
            else:
                out_data_high_vpd = pd.concat([
                    out_data_high_vpd,
                    new_data_high_vpd
                    ],
                    axis = 0
                )

            if out_data_extreme_vpd.empty:
                # create the out dataframe
                out_data_extreme_vpd = new_data_extreme_vpd
            else:
                out_data_extreme_vpd = pd.concat([
                    out_data_extreme_vpd,
                    new_data_extreme_vpd
                    ],
                    axis = 0
                )

    # save output csv with id as single row
    out_data_high_vpd.to_csv(here(f'data/csv_data/{name}/final_data/high_vpd_days.csv'))
    out_data_extreme_vpd.to_csv(here(f'data/csv_data/{name}/final_data/extreme_vpd_days.csv'))