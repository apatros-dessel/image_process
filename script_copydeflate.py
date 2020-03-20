# -*- coding: utf-8 -*-

import os
import gdal

dir_in = r'd:\resursp_new\pan'
dir_out = r'e:\resursp_new\pansharpened\Krym_new'

file_list = os.listdir(dir_in)

print('%i files found' % len(file_list))

for i, file in enumerate(file_list):

    path_in = os.path.join(dir_in, file)
    ds_in = gdal.Open(path_in)

    if ds_in is None:
        print('Cannot open file', file)
        continue

    if not os.path.exists(dir_out):
        os.makedirs(dir_out)

    driver = gdal.GetDriverByName('GTiff')
    print(['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'TILED=YES', 'BIGTIFF=YES'])
    driver.CreateCopy(os.path.join(dir_out, file), ds_in, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'TILED=YES', 'BIGTIFF=YES'])
    print('{} File written {}'.format(i, file))

