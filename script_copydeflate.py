# -*- coding: utf-8 -*-

import os
import gdal

dir_in = r'e:\kanopus_new\pansharpened\Krym'
dir_out = r'e:\kanopus_new\pansharpened\Krym_def'

for file in os.listdir(dir_in):

    path_in = os.path.join(dir_in, file)
    ds_in = gdal.Open(path_in)

    if ds_in is None:
        print('Cannot open file', file)
        continue

    if not os.path.exists(dir_out):
        os.makedirs(dir_out)

    driver = gdal.GetDriverByName('GTiff')
    driver.CreateCopy(os.path.join(dir_out, '!'+file), ds_in, options = ['COMPRESS=DEFLATE', 'ZLEVEL=9'])
    print('File written', file)
