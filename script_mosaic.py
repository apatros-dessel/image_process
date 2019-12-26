# -*- coding: utf-8 -*-

from image_processor import *
import gdal

input_path = r'c:\sadkov\toropez\planet\20190516'
# input_path = r'c:\sadkov\toropez\planet\20190516\2367219_3665010_2019-05-16_1011'
output_path = r'c:\sadkov\toropez\image_test'

path2composite = r'{}\composite'.format(output_path)
path2rgb = r'{}\rgb'.format(output_path)

proc = process(output_path=output_path)
proc.input(input_path)

strip_band_paths = OrderedDict()

for ascene in proc.scenes:
    date_sat = ascene.meta.name('Mosaic_[date]_[sat]_LZW')
    if date_sat not in strip_band_paths:
        strip_band_paths[date_sat] = [ascene.get_raster_path('Analytic')]
    else:
        strip_band_paths[date_sat].append(ascene.get_raster_path('Analytic'))

scroll(strip_band_paths)

for date_sat in strip_band_paths:

    # geodata.Mosaic(strip_band_paths[date_sat], fullpath(output_path, date_sat, 'tif'), band_num=4, options = ['COMPRESS=LZW', 'BIGTIFF=YES'])

    '''
    path2raster_list = strip_band_paths[date_sat]
    raster_limits = geodata.RasterLimits(path2raster_list, method=2, band_limits=(0.02, 0.98), enforce_nodata=0)
    print(raster_limits)

    if np.nan in raster_limits:
        print('Incorrect limits for {}: {}'.format(date_sat, raster_limits))
        continue

    path2rgb_folder = r'{}\{}'.format(path2rgb, date_sat)

    if not os.path.exists(path2rgb_folder):
        os.makedirs(path2rgb_folder)

    with open(r'{}\limits.txt'.format(path2rgb_folder), 'w') as limlog:
        limlog.write(str(raster_limits))

    for path2raster in path2raster_list:
        file = os.path.split(path2raster)[1]

        path2rgb_image = r'{}\{}_RGB.tif'.format(path2rgb_folder, file[:-4])

        try:
            geodata.RasterToImage(path2raster, path2rgb_image, method=-1, band_limits=raster_limits, gamma=0.5, band_order=[3, 2, 1], compress='LERC_DEFLATE', enforce_nodata=0)
        except:
            print('Error making RGB: {}'.format(path2rgb))
        '''

    pass

