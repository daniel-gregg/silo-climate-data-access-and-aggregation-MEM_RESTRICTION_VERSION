## Allowable data specificaitons for the user-specified data-dict

def data_dict():
    
    data = {
        'silo_climate_vars' : {
            'monthly_rainfall' : [x for x in range(1889,2024,1)],
            'daily_rainfall' : [x for x in range(1889,2024,1)],
            'morton_actual_evapotranspiration' : [x for x in range(1889,2024,1)],
            'morton_potential_evapotranspiration' : [x for x in range(1889,2024,1)],
            'morton_wet_area_potential_evapotranspiration' : [x for x in range(1889,2024,1)],
            'max_temp' : [x for x in range(1889,2024,1)],
            'min_temp' : [x for x in range(1889,2024,1)],
            'vapour_pressure' : [x for x in range(1889,2024,1)],
            'vapour_pressure_deficit' : [x for x in range(1889,2024,1)],
            'pan_evaporation_class_a' : [x for x in range(1970, 2024, 1)],
            'synthetic_evaporation' : [x for x in range(1889,2024,1)],
            'combination_evaporation' : [x for x in range(1889,2024,1)],
            'morton_shallow_lake_evaporation' : [x for x in range(1889,2024,1)],
            'relative_humidity_at_max_temp' : [x for x in range(1889,2024,1)],
            'relative_humidity_at_min_temp' : [x for x in range(1889,2024,1)],
            'FAO_evapotranspiration_short_crop' : [x for x in range(1889,2024,1)],
            'ASCE_evapotranspiration_tall_crop' : [x for x in range(1889,2024,1)],
            'mean_sea_level_atmospheric_pressure' : [x for x in range(1957, 2024, 1)],
            'solar_radiation' : [x for x in range(1889,2024,1)]
        },
        'ndvi_vars' : [],
        'bom_vars' : ['soil_moisture'],
        'statistical_areas' : ['sa1', 'sa2', 'sa3', 'sa4'], #list that must include at least one of these (and up to all of) 
        'regions_subsets' : ['ACT','NSW','VIC','TAS','SA','WA','NT','QLD','southern_growing_region'],
    }