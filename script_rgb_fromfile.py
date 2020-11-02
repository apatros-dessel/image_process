# -*- coding: utf-8 -*-

from image_processor import *

# path_in = r'i:\rks\kanopus_cherepan\Samara'
path_in = r'e:\resursp_new\pansharpened\Krym_new'
path_out = r'e:\resursp_new\rgb\Krym'

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
    # if not file.endswith('14.tif'):
        # continue
    res = geodata.RasterToImage3(fullpath(path_in, file),
                           fullpath(path_out, file.replace('_modified','.RGB')),
                           method=2,
                           band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                           gamma=0.85,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=[3, 2, 1],
                           GaussianBlur=False,
                           reprojectEPSG=3857,
                           reproject_method=geodata.gdal.GRA_Lanczos,
                           compress='DEFLATE',
                           overwrite=True,
                           alpha=True)
    if res == 0:
        print('{} File written: {}'.format(i+1, file))
    else:
        print('{} Error making RGB: {}'.format(i+1, file))
