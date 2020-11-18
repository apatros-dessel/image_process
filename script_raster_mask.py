# -*- coding: utf-8 -*-

from image_processor import *

path2raster = r'c:\sadkov\toropez\image_test\Mosaic_20190516_1011_LZW.tif'
path2export = r'c:\sadkov\toropez\image_test\Mosaic_20190516_1011_LZW_mask.shp'
shp_name = r'planet_cover.shp'
report_name = r'planet_cover.xls'

geodata.RasterDataMask(path2raster, path2export, use_nodata = True, enforce_nodata = 0, alpha=None, dst_fieldname = None, overwrite = True)