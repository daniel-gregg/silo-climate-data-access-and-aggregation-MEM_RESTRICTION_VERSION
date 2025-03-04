### Accesses the BOM data catalogue

### Codes for AWRAL V7 (this took an insane amount of googling to find..)
# src: https://awo.bom.gov.au/assets/notes/publications/Oke_AWRACMS_User_Guide.pdf
# Check the appendix

# 'dd' -> deep drainage
# 'e0' -> potential evaporation
# 'etot' -> total evapotranspiration
# 'es' -> evaporation flux 
# 'qtot' -> total discharge to stream (seems to be 'runoff' in the diagram linked below)
# 's0' -> water content store of the soil surface portion in millimetres# 
# 'ss' -> water content of the shallow soil portion in millimetres
# 'sd' -> water content store of the deep soil portion in millimetres

# for a diagram of these elements see here:
#https://awo.bom.gov.au/about/overview/historical#historical-water-balance-information

# codes in the catalogue are arranged as:
# 'code_yyyy.nc' where 'yyyy' is a four-character year variable (e.g. '2019'). 
# years range from 1911 to current updated monthly

# code below sourced from :
# https://gist.github.com/hot007/2e482b951603670f24ee03b4e7de4b9f

import xarray as xr
from siphon.catalog import TDSCatalog
import matplotlib.pyplot as plt

# get filelist
cat = TDSCatalog('https://thredds.nci.org.au/thredds/catalog/iu04/australian-water-outlook/historical/v1/AWRALv7/catalog.xml')
print("\n".join(cat.datasets.keys()))
filelist=[x for x in cat.datasets]

# subset for target elements using codes
filelist = [x for x in filelist if 's0' in x or 'ss' in x]

# subset for target years
years = [str(x) for x in range(2001,2025+1)]
filelist = [x for x in filelist if any(x.split("_")[1].split(".")[0] in year for year in years)]

# download.
BOM_DAP_root='https://thredds.nci.org.au/thredds/dodsC/iu04/australian-water-outlook/historical/v1/AWRALv7/'
paths = [ BOM_DAP_root+f for f in filelist]

for path in paths:
    data = xr.open_mfdataset(paths, combine='by_coords',parallel=True)#,chunks={"time": 744}) #This bit is slooooow! Start it and wander off for a long while (20min-2hrs?).

# from the gist: (delete once sorted)
#DAProot='http://data-cbr.csiro.au/thredds/dodsC/catch_all/CMAR_CAWCR-Wave_archive/CAWCR_Wave_Hindcast_1979-2010/gridded/'




data