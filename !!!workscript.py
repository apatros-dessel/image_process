from image_processor import *
'''
path = [
    # r'F:/rks/toropez/image_test/full/Mosaic_20190905_0f31_DEFLATE.tif',
    # r'f:\rks\tver',
    r'f:\rks\tver\20190911',
    # r'f:\rks\tver\20190911\20190911_062630_100d',
    ]

out = r'd:\digital_earth\planet_rgb'

proc = process()
proc.input(path)

for ascene in proc.scenes:

    refpaths = []

    for band_id in ['red', 'green', 'blue', 'nir']:
        refpaths.append(ascene.get_product_path('Reflectance', band_id, set_product_path=out, set_name='{}-[fullsat]-[date]-[location]-[lvl].tif'.format(band_id.upper())))

    path2export = fullpath(out, ascene.meta.name(r'RF4-[fullsat]-[date]-[location]-[lvl].tif'))
    geodata.raster2raster(refpaths, path2export, path2target=None, method=geodata.gdal.GRA_NearestNeighbour, exclude_nodata=True, enforce_nodata=None, compress='LZW', overwrite=True)
'''

path2oldband = [(r'e:\test\newsnt\S2A_MSIL1C_20150822_NDVI_DOS1.tif', 1)]
path2newband = [(r'e:\test\newsnt\S2B_MSIL1C_20180801_NDVI_DOS1.tif', 1)]
path2oldband = (r'e:\test\newsnt\S2B_MSIL1C_20180801_NDVI_DOS1.tif', 1)
path2newband = (r'e:\test\newsnt\S2A_MSIL2A_20190828_NDVI_DOS1.tif', 1)
min_path = r'e:\test\test_minus.tif'
# quot_path = r'e:\test\test_quot.tif'
path2shp = r'e:\test\test_change.shp'

geodata.band_difference(path2oldband, path2newband, min_path, nodata = 0, compress = None, overwrite = True)
# geodata.band_quot(path2oldband, path2newband, quot_path, nodata = 0, compress = None, overwrite = True)

geodata.save_to_shp(min_path, path2shp, band_num = 1, classify_table = [[None, -0.1, -1], [0.1, None, 1]], export_values = None, overwrite = True)

# geodata.Changes(path2oldband, path2newband, min_path, calc_path = None, formula = 0, lower_lims = None, upper_lims = None, check_all_values = False, upper_priority = True)
