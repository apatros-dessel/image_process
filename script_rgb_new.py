# -*- coding: utf-8 -*-

from image_processor import *

path = [
    r'd:\digital_earth\kanopus_new\krym',
    # r'f:\rks\tver',
    # r'f:\rks\tver\20190912',
    # r'f:\rks\tver\20190911\20190911_062630_100d',
    # r'f:\rks\tver\20190911\20190911_062629_100d',
    # r'f:\rks\tver\20190910',
    ]

# folder = r'd:\digital_earth\planet_rgb\new'
folder = r'e:\kanopus_new'

if not os.path.exists(folder):
    os.makedirs(folder)


proc = process()
proc.input(path)

raster_path_dict = {}
print('Start making rgb from %i scenes' % len(proc))

for ascene in proc.scenes:

    if not '.PMS.' in ascene.meta.id:
        continue

    strip_id = ascene.meta.name('[sat]-[date]')

    if strip_id in raster_path_dict:
        raster_path_dict[strip_id].append(ascene.get_raster_path('mul'))
    else:
        raster_path_dict[strip_id] = [ascene.get_raster_path('mul')]

scroll(raster_path_dict, header='Raster paths:')

errors_list = []

# border_list = geodata.GetRasterPercentiles(raster_path_dict[raster_path_dict.keys()[0]], min_percent = 0.01, max_percent = 0.995, band_num_list = [3,2,1], nodata = 0)

# print(border_list)


for strip_id in raster_path_dict:

    raster_path_list = raster_path_dict[strip_id]
    # band_hist_dict = [{},{},{}]
    # borders_list = []

    path2export_list = []
    for path2raster in raster_path_list:
        path2export = r'{}\{}\{}'.format(folder, strip_id[-8:], os.path.split(path2raster)[1])
        if os.path.exists(path2export):
            print('File already exists: {}'.format(path2export))
        else:
            path2export_list.append((path2raster, path2export))

    if len(path2export_list) == 0:
        continue

    borders_list = geodata.GetRasterPercentiles(raster_path_list, min_percent = 0.01, max_percent = 0.995, band_num_list = [3,2,1], nodata = 0)

    print('Start processing %i scenes' % len(path2export_list))

    for path2raster, path2export in path2export_list:
        if not os.path.exists(os.path.split(path2export)[0]):
            os.makedirs(os.path.split(path2export)[0])
        # path2export = r'{}\{}'.format(folder, os.path.split(path2raster)[1])
        # res = geodata.RasterToImage3(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], reprojectEPSG=3857, compress='LZW', overwrite=False, alpha=False)

        try:
            # res = geodata.RasterToImage2(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], compress='LZW', overwrite=False, alpha=False)
            res = geodata.RasterToImage3(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], reprojectEPSG = 3857, compress='LZW', overwrite=False, alpha=False)
        except:
            res = 1
        if res == 0:
            print('File written: {}'.format(path2export))
        else:
            print('Failed to write file: {}'.format(path2export))
            errors_list.append(path2export)

if len(errors_list) > 0:
    scroll(errors_list, header='Errors while procesing files:')

