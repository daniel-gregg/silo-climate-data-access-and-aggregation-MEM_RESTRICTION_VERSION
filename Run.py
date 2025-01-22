## Head script that calls modules - aim to turn into API function in the future

#core modules/packages
import sys
import os
from pyprojroot.here import here
from pathlib import Path

## Setting things up
#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.get_data.get_and_update_data import get_and_refresh_data

### Get data
get_and_refresh_data()
