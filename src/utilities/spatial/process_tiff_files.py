
from src.utilities.spatial.get_zonal_statistics_and_rasters import get_zonal_statistics_and_rasters

def process_tiff_files(files_to_process):
    
    # ask user for permission to proceed
    user_input = input("Do you want to continue? (yes/no): ")
    if user_input.lower() == "yes" or user_input.lower() == "y":
        print("Processing files ... (this may take some time)")
    else:
        print("Exiting...")
        return ()
    
    """ # this loop will only process data for False entries in the above dictionary (i.e. present in data/climate_data but not data/tiff_files)
    for sa_scope in varnames_present_in_processed_data.keys():
        sa_scope_sub_dict = varnames_present_in_processed_data[sa_scope]
        for var in sa_scope_sub_dict.keys():
            sa_scope_var_sub_dict = sa_scope_sub_dict[var]
            for year in sa_scope_var_sub_dict[year]:
                get_zonal_statistics_and_rasters(sa_scope, var, year)
                #should print 'processed data for ABS {sa_scope} for variable {var} for year {year}       
    """


    return 'done'



