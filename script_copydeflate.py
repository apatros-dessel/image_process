# -*- coding: utf-8 -*-

import os
import gdal

dir_in = r'e:\rks\digital_earth\pari\TCP-PMS-8CH'
dir_out = r'e:\rks\digital_earth\pari\Krym\TCP-PMS-8CH'

file_list = os.listdir(dir_in)

print('%i files found' % len(file_list))

if not os.path.exists(dir_out):
    os.makedirs(dir_out)

for i, file in enumerate(file_list):

    if os.path.exists(os.path.join(dir_out, file)):
        print(r'{} File already exists: {}'.format(i+1, file))
        continue

    path_in = os.path.join(dir_in, file)
    ds_in = gdal.Open(path_in)

    if ds_in is None:
        print('Cannot open file', file)
        continue

    driver = gdal.GetDriverByName('GTiff')
    print(['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'TILED=YES', 'BIGTIFF=YES'])
    driver.CreateCopy(os.path.join(dir_out, file), ds_in, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'TILED=YES', 'BIGTIFF=YES'])
    print('{} File written {}'.format(i+1, file))

