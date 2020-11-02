# -*- coding: utf-8 -*-

from image_processor import *

path2oldband = [(r'e:\test\newsnt\S2B_MSIL1C_20180801_NDVI_DOS1.tif', 1)]
path2newband = [(r'e:\test\newsnt\S2A_MSIL2A_20190828_NDVI_DOS1.tif', 1)]
# path2oldband = (r'e:\test\newsnt\S2B_MSIL1C_20180801_NDVI_DOS1.tif', 1)
# path2newband = (r'e:\test\newsnt\S2A_MSIL2A_20190828_NDVI_DOS1.tif', 1)
min_path = r'e:\test\test_minus_noblur.tif'
# quot_path = r'e:\test\test_quot.tif'
class_path = r'e:\test\test_class_noblur.tif'
path2shp = r'e:\test\test_change.shp'

# geodata.band_difference(path2oldband, path2newband, min_path, nodata = 0, compress = None, overwrite = True)
# geodata.band_quot(path2oldband, path2newband, quot_path, nodata = 0, compress = None, overwrite = True)

# geodata.ClassifyBandValues((min_path, 1), (class_path, 3), classify_table = [(None, -0.1, -1), (0.1, None, 1)], nodata = 0, compress = 'LZW', overwrite = True)
# geodata.ClassifyBandValues(path2oldband, (class_path, 2), classify_table = [(0, 0.1, 1), (0.1, 0.5, 2), (0.5, 0.6, 3), (0.6, 0.7, 4), (0.7, 0.8, 5), (0.8, 1, 10)], nodata = 0, compress = 'LZW', overwrite = True)
# geodata.ClassifyBandValues(path2newband, (class_path, 1), classify_table = [(0, 0.1, 1), (0.1, 0.5, 2), (0.5, 0.6, 3), (0.6, 0.7, 4), (0.7, 0.8, 5), (0.8, 1, 10)], nodata = 0, compress = 'LZW', overwrite = True)


# geodata.save_to_shp(min_path, path2shp, band_num = 1, classify_table = [[None, -0.1, -1], [0.1, None, 1]], export_values = None, overwrite = True)
# geodata.VectorizeBand((min_path, 1), path2shp, classify_table = [[None, -0.1, -1], [0.1, None, 1]], erode_val=1, overwrite = True)

geodata.Changes(path2oldband, path2newband, class_path, calc_path = min_path, formula = 1, check_all_values = False, upper_priority = True, GaussianBlur=False)
