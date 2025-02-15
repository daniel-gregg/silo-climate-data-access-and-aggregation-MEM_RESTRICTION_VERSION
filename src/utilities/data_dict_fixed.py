## Allowable data specificaitons for the user-specified data-dict

# and include them in the 
def state_scope(state, sa_scope):
    # state is a string acronym for state (i.e. NSW, ACT, QLD, WA, SA, NT, TAS, VIC)
    # statistical_area_scope is which scope to use (i.e. 'sa1', 'sa2', 'sa3', 'sa4')
    
    sa_scope_df = get_sa_codes(sa_scope)
    
    if state == 'NSW':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['1']]
    if state == 'QLD':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['3']]
    if state == 'SA':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['4']]
    if state == 'WA':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['5']]
    if state == 'TAS':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['6']]
    if state == 'ACT':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['7']]
    if state == 'NT':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['8']]
    if state == 'VIC':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['2']]

    return sa_regions

def southern_growing_region(sa_scope):
    # this comprises SA, VIC, TAS

    sa_scope_df = get_sa_codes(sa_scope)

    sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['2', '4', '6']]
    
    return sa_regions

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
        'statistical_areas' : {
            'state_scope': state_scope,
            'southern_growing_region': southern_growing_region
        }
    }