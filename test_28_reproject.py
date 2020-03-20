from geodata import *

path_in = r'C:/Users/admin/Desktop/LC08_L1TP_176028_20190820_20190903_01_T1.tif'
path_out = r'e:\test\landsat.tif'

ReprojectRaster(path_in, path_out, 3857, method = gdal.GRA_Lanczos, compress = 'DEFLATE', overwrite = True)