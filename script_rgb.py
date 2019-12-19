# -*- coding: utf-8 -*-

from image_processor import *

path = r'c:\sadkov\minprod\planet\composites\2019-09-10'
folder = r'c:\sadkov\minprod\planet\composites\2019-09-10\image'

if not os.path.exists(folder):
    os.makedirs(folder)

path2raster_list = os.listdir(path)

print('Start processing %i files' % len(path2raster_list))

for name in path2raster_list:

    synt_dict = {
        # '1054': [(1500, 2900), (2700, 3900), (3400, 4500)],
        # '0f22': [(1900, 2900), (3000, 4100), (3500, 4400)],
        # '1014': [(1900, 3100), (3100, 4100), (3500, 4300)],
        # '105e': [(1600, 3000), (3000, 4800), (4400, 5600)],
        '0f2a': [(1600, 4100), (2600, 4900), (3500, 5800)],
        '101e': [(2100, 4500), (3300, 5100), (4100, 5800)],
        # '0f2a': [(0, 5000), (0, 6500), (0, 7500)],
        # '101e': [(0, 6000), (0, 7700), (0, 8800)],
        '0f2b': [(2300, 3300), (3600, 4500), (4300, 5200)],
        '1035': [(150, 1200), (200, 1000), (100, 800)],
        '0f15': [(200, 1000), (200, 820), (100, 580)],
        '0f31': [(200, 1150), (200, 840), (100, 600)],
        '0f31': [(200, 1150), (200, 840), (100, 600)],
    }

    path2raster = fullpath(path, name)
    path2export = fullpath(folder, name)
    band_limits = None
    for key in synt_dict:
        if '_%s_' % key in name:
            band_limits = synt_dict[key]
            break
    if band_limits is not None:
        geodata.raster_to_image(path2raster, path2export, band_limits, gamma=0.85, exclude_nodata = True, enforce_nodata = 0, compress='LERC_DEFLATE')
        print('Finished: {}'.format(path2export))
    else:
        print('Band limits not found for: {}'.format(name))