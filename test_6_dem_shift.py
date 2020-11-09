# Shifts DEM to minimize difference with another one
# !!! Does not perform reprojection, just shifts raster adding new lines by spline !!!

from fill_dem import *
import os
import gdal

path = r'C:\sadkov\forest\Sept_test\dem\kluchevskoie\tif'
dem1_name = r'DEM_alos_Kluchevskoie.tif'
dem2_name = r'DEM_topo_Kluchevskoie.tif'
dem2_new_name = 'dem_topo_Kluchevskoie_shifted2alos.tif'

os.chdir(path)
source_dem = gdal.Open(dem1_name)
dem1 = source_dem.GetRasterBand(1).ReadAsArray()
dem2 = gdal.Open(dem2_name).ReadAsArray()

dem2_new = shift(dem1, dem2)

driver = gdal.GetDriverByName('GTiff')
source_dem2 = gdal.Open(dem2_name)
outData = driver.CreateCopy(dem2_new_name, source_dem2)
#outData.AddBand(gdal.GDT_Float32)
outData.GetRasterBand(1).WriteArray(dem2_new)
outData = None
