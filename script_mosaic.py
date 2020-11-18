# -*- coding: utf-8 -*-

from image_processor import *

# input_path = r'c:\sadkov\toropez\planet\20190516'
input_path_list = [r'c:\sadkov\toropez\planet',
                   r'd:\rks\toropez\planet']
output_path = r'c:\sadkov\toropez\image_test\full'

path2composite = r'{}\composite'.format(output_path)
path2rgb = r'{}\rgb'.format(output_path)

proc = process(output_path=output_path)
# proc.input(input_path)
for in_path in input_path_list:
    proc.input(in_path, imsys_list=['PLN'])

strip_band_paths = OrderedDict()

for ascene in proc.scenes:
    date_sat = ascene.meta.name('Mosaic_[date]_[sat]_DEFLATE')
    if date_sat not in strip_band_paths:
        strip_band_paths[date_sat] = [ascene.get_raster_path('Analytic')]
    else:
        strip_band_paths[date_sat].append(ascene.get_raster_path('Analytic'))

for i, date_sat in enumerate(strip_band_paths.keys()[100:]):

    # Make a mosaic
    geodata.Mosaic(strip_band_paths[date_sat], fullpath(output_path, date_sat, 'tif'), band_num=4, options = ['COMPRESS=DEFLATE', 'BIGTIFF=YES'])

    # Make a vector cover for a mosaic
    geodata.RasterDataMask(fullpath(output_path, date_sat, 'tif'), fullpath(output_path, date_sat, 'shp'), enforce_nodata=0)

    print('Finished %i' % i)
