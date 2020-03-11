from geodata import *

path_in = r'C:/Users/admin/AppData/Local/Temp/image_processor/40/86/0.tif'
path_out = r'C:/Users/admin/Desktop/010.tif'

ReprojectRaster(path_in, path_out, 3857, method = gdal.GRA_Lanczos, compress = 'DEFLATE', overwrite = True)