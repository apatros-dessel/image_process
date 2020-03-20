from geodata import *

path_in = r'C:/Users/admin/Desktop/030_REPR_REPR_ZERO.tif'
path_out = r'C:/Users/admin/Desktop/060_QUICK_4326.tif'

# CopyToJPG(path_in, path_out)
'''
ds_in = gdal.Open(path_in)
driver = gdal.GetDriverByName('GTiff')
ds_out = driver.CreateCopy(path_out, ds_in, options = ['COMPRESS=JPEG'])
ds_out = None
'''

path_in_list = folder_paths(r'd:\kanopus_new\rgb\Krym')[1]

for path_in in path_in_list:
    MakeQuicklook(path_in, fullpath(r'd:\kanopus_new\quicklook\Krym', os.path.split(path_in)[1]), 3857, pixelsize=60)