from geodata import *

pin = r'e:\rks\razmetka\set007__20210302__landsat_sentinel__edit001\images'
replace = {32767:0}

files = folder_paths(pin,1,'tif')

for file in files:
    # ReplaceValues(file, replace)
    raster = gdal.Open(file)
    print(split3(file)[1], np.unique(raster.ReadAsArray())[-1])