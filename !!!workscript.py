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

path2oldband = (r'D:\digital_earth\sentinel_crops\S2B_MSIL2A_20190604T084609_N0212_R107_T37VCD_20190604T121704.SAFE\GRANULE\L2A_T37VCD_A011716_20190604T085141\IMG_DATA\R10m\T37VCD_20190604T084609_B08_10m.jp2', 1)
path2newband = (r'D:\digital_earth\sentinel_crops\S2A_MSIL2A_20190828T084601_N0213_R107_T37VCD_20190828T131555.SAFE\GRANULE\L2A_T37VCD_A021840_20190828T084904\IMG_DATA\R10m\T37VCD_20190828T084601_B08_10m.jp2', 1)
min_path = r'e:\test\test_minus.tif'
quot_path = r'e:\test\test_quot.tif'

geodata.band_difference(path2oldband, path2newband, min_path, nodata = 0, compress = None, overwrite = True)
geodata.band_quot(path2oldband, path2newband, quot_path, nodata = 0, compress = None, overwrite = True)
