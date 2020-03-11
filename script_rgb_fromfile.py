# -*- coding: utf-8 -*-

from image_processor import *

# path_in = r'i:\rks\kanopus_cherepan\Samara'
path_in = r'e:\kanopus_new\pansharpened\Tver_pan'
path_out = r'd:\kanopus_new\rgb\Tver_new'

raster_list = []
if os.path.exists(path_in):
    for file in os.listdir(path_in):
        if file.endswith('.tif'):
            raster_list.append(file)
if len(raster_list)>0:
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    print('Start making RGB for %i files' % len(raster_list))

for i, file in enumerate(raster_list):
    res = geodata.RasterToImage3(fullpath(path_in, file),
                           fullpath(path_out, file),
                           method=2,
                           band_limits=[(0.01, 0.9995), (0.01, 0.9995), (0.01, 0.9995)],
                           gamma=0.85,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=[1, 2, 3],
                           GaussianBlur=False,
                           reprojectEPSG=3857,
                           reproject_method=geodata.gdal.GRA_Lanczos,
                           compress='DEFLATE',
                           overwrite=False,
                           alpha=False)
    if res == 0:
        print('{} File written: {}'.format(i, file))
    else:
        print('() Error makcGB: {}'.format(i, file))