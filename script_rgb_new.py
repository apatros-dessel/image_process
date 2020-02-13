# -*- coding: utf-8 -*-

from image_processor import *

path = [
    # r'F:/rks/toropez/image_test/full/Mosaic_20190905_0f31_DEFLATE.tif',
    # r'f:\rks\tver',
    r'f:\rks\tver\20190912',
    # r'f:\rks\tver\20190911\20190911_062630_100d',
    # r'f:\rks\tver\20190911\20190911_062629_100d',
    # r'f:\rks\tver\20190910',
    ]

folder = r'd:\digital_earth\planet_rgb\new\20190912'


proc = process()
proc.input(path)

raster_path_dict = {}


for ascene in proc.scenes:

    strip_id = ascene.meta.name('[sat]-[date]')
    raster_path = ascene.get_raster_path('Analytic')

    if strip_id in raster_path_dict:
        raster_path_dict[strip_id].append(raster_path)
    else:
        raster_path_dict[strip_id] = [raster_path]

'''
raster_path_dict = {
    'strip_id': [
        r'e:\rks\digital_earth\neuro\20190912_082257_1038_3B_AnalyticMS.tif',
    ]
}
'''

scroll(raster_path_dict)

errors_list = []

for strip_id in raster_path_dict:

    raster_path_list = raster_path_dict[strip_id]
    band_hist_dict = [{},{},{}]
    borders_list = []

    path2export_list = []
    for path2raster in raster_path_list:
        path2export = r'{}\{}'.format(folder, os.path.split(path2raster)[1])
        if os.path.exists(path2export):
            print('File already exists: {}'.format(path2export))
        else:
            path2export_list.append((path2raster, path2export))

    if len(path2export_list) == 0:
        continue

    for raster_path in raster_path_list:

        ds = geodata.gdal.Open(raster_path)

        if ds is None:
            continue

        for bandnum in [2,1,0]:

            raster_array = ds.GetRasterBand(bandnum+1).ReadAsArray()
            values, number = np.unique(raster_array, return_counts=True)

            for val, num in zip(values, number):
                # print(val, num)
                if val in band_hist_dict[bandnum]:
                    band_hist_dict[bandnum][val] += num
                else:
                    band_hist_dict[bandnum][val] = num

    for band_num_dict in band_hist_dict:

        try:

            if len(band_num_dict) == 1:
                print('Cannot build histogram for:')
                scroll(raster_path_list)
                continue

            if 0 in band_num_dict:
                band_num_dict.pop(0)

            band_vals = np.array(band_num_dict.keys())
            # band_vals.sort()
            band_order = band_vals.argsort()
            band_vals = band_vals[band_order]
            band_nums = np.array(band_num_dict.values())[band_order]
            pixel_sum = np.sum(band_nums)

            num_min = pixel_sum * 0.01
            num_max = pixel_sum * 0.995
            num_max_inv = pixel_sum - num_max

            min_mask = band_vals

            sum = 0
            i = 0
            while sum < num_min:
                i += 1
                sum += band_nums[i]
            min_val = band_vals[i]

            band_vals = band_vals[::-1]
            band_nums = band_nums[::-1]

            sum = 0
            i = 0
            while sum < num_max_inv:
                i += 1
                sum += band_nums[i]
            max_val = band_vals[i]

        except:
            print('Cannot calculate limits for {}'.format(strip_id))
            min_val = 0
            max_val = 10000

        borders_list.append((min_val, max_val))
        print(min_val, max_val)

    for path2raster, path2export in path2export_list:
        # path2export = r'{}\{}'.format(folder, os.path.split(path2raster)[1])
        try:
            res = geodata.RasterToImage2(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], compress='LZW', overwrite=False, alpha=False)
        except:
            res = 1
        if res == 0:
            print('File written: {}'.format(path2export))
        else:
            print('Failed to write file: {}'.format(path2export))
            errors_list.append(path2export)

if len(errors_list) > 0:
    scroll(errors_list, header='Errors while procesing files:')

