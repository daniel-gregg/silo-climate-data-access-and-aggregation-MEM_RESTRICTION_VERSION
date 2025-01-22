## Dictionary mapping for silo/boto3 variables to file names

def get_silo_vars_dict_mapping():
    silo_dict = {
        'monthly_rainfall' : 'monthly_rain',
        'daily_rainfall' : 'daily_rain',
        'morton_actual_evapotranspiration' : 'et_morton_actual',
        'morton_potential_evapotranspiration' : 'et_morton_potential	',
        'morton_wet_area_potential_evapotranspiration' : 'et_morton_wet',
        'max_temp' : 'max_temp',
        'min_temp' : 'min_temp',
        'vapour_pressure' : 'vp',
        'vapour_pressure_deficit' : 'vp_deficit',
        'pan_evaporation_class_a' : 'evap_pan',
        'synthetic_evaporation' : 'evap_syn',
        'combination_evaporation' : 'evap_comb',
        'morton_shallow_lake_evaporation' : 'evap_morton_lake',
        'relative_humidity_at_max_temp' : 'rh_tmax',
        'relative_humidity_at_min_temp' : 'rh_tmin',
        'FAO_evapotranspiration_short_crop' : 'et_short_crop',
        'ASCE_evapotranspiration_tall_crop' : 'et_tall_crop',
        'mean_sea_level_atmospheric_pressure' : 'mslp',
        'solar_radiation' : 'radiation'
    }

    return silo_dict
