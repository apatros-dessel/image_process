# -*- coding: utf-8 -*-

from image_processor import *

path_in = r''
path_out = r''

files_list = os.listdir(path_in)

for i, file in enumerate(files_list):

    file_base = os.path.basename(file)

    geodata.RasterDataMask(fullpath(path_in, file), fullpath(path_out, file_base, 'shp'), enforce_nodata=0)