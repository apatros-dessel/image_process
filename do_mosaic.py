# -*- coding: utf-8 -*-

from image_processor import *

input_path = r'c:\sadkov\s2glc'
output_path = r'{}\mosaic_full.tiff'.format(input_path)

input_path_list = os.listdir(input_path)

for i in range(len(input_path_list)-1, -1, -1):
    if not input_path_list[i].endswith('.tif'):
        input_path_list.pop(i)
    else:
        input_path_list[i] = fullpath(input_path, input_path_list[i])

scroll(input_path_list)

geodata.Mosaic(input_path_list, output_path, band_num=1, options = ['COMPRESS=DEFLATE'])