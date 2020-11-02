# -*- coding: utf-8 -*-

from image_processor import *
from PIL import Image

path = r'e:\export_test\examples\Kanopus\Krym'
band_num_list = [1,2,3,4]
path2xls = r'e:\test\Kanopus_hist.xls'

proc = process().input(path)
# band_hist_dict = OrderedDict()

for ascene in proc.scenes:

    path = ascene.get_band_path('red')[0]
    bandpath = []
    band_hist_dict = OrderedDict()

    for band_num in band_num_list:
        bandpath.append((path, band_num))

    raster_data = geodata.MultiRasterData(bandpath, data=(0, 2))

    for band_num, data_arr in raster_data:
        # key = '{}_{}'.format(os.path.basename(path), band_num)
        band_hist_dict['{}_{}'.format(os.path.basename(path), band_num)] = arrendict(data_arr)

    print('Finished processind scene: {}'.format(ascene.meta.id))

# dict_to_xls(path2xls, band_hist_dict)
