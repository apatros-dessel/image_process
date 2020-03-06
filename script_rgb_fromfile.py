# -*- coding: utf-8 -*-

from image_processor import *

path_in = r'i:\rks\kanopus_cherepan\Samara'
path_out = r'e:\kanopus_new\rgb\Samara'

raster_list = []
if os.path.exists(path_in):
    for file in os.listdir(path_in):
        if file.endswith('.tif'):
            raster_list.append(file)
if len(raster_list)>0:
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    print('Start making RGB for %i files' % len(raster_list))

for file in raster_list:
    res = geodata.RasterToImage3(fullpath(path_in, file),
                           fullpath(path_out, file),
                           method=2,
                           band_limits=[(0.01, 0.9995), (0.01, 0.9995), (0.01, 0.9995)],
                           gamma=0.85,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=[1, 2, 3],
                           reprojectEPSG=3857,
                           reproject_method=geodata.gdal.GRA_Lanczos,
                           compress='DEFLATE',
                           overwrite=True,
                           alpha=False)
    if res == 0:
        print('File written: {}'.format(file))
    else:
        print('Error making RGB: {}'.format(file))