# -*- coding: utf-8 -*-

# Makes shapefile of water bodies from Landsat or Sentinel data using image_process module

from ndwi_process import *
from datetime import datetime

input_path = r'C:\source\sentinel\T48VVK\S2A_MSIL1C_20160716T042712_N0204_R133_T48VVK_20160716T042707.SAFE'
output_path = r'C:\Temp'
dem_path = r'C:\source\srtm\srtm_57_01\srtm_57_01.tif'

proc = process(input_path=input_path, output_path=output_path, vectorize=True)
proc.input()
print(proc)

if proc[0]:
    proc[0].path2dem = dem_path
    proc.vectorize = True
    proc.run('ndwi')
