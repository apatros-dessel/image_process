from image_processor import *

path = [
    # r'F:/rks/toropez/image_test/full/Mosaic_20190905_0f31_DEFLATE.tif',
    # r'f:\rks\tver',
    # r'f:\rks\tver\20190911',
    # r'f:\rks\tver\20190911\20190911_062630_100d',
    # r'f:\rks\tver\20190911\20190911_062629_100d',
    r'f:\rks\toropez\planet\20190727\2552959_3665209_2019-07-27_104b',
    ]

out = r'd:\digital_earth\planet_ref'

if not os.path.exists(out):
    os.makedirs(out)


proc = process(output_path=out)
proc.input(path)

for ascene in proc.scenes:

    # bandpaths = []

    refpaths = []
    for band_id in [
        'red',
        'green',
        'blue',
        'nir'
    ]:

        refpaths.append(ascene.get_product_path('Reflectance', band_id, set_product_path=out, set_name='{}-[fullsat]-[date]-[location]-[lvl].tif'.format(band_id.upper())))
        # bandpath_in = ascene.get_band_path(band_id)
        # bandpath_out = (r'{}\{}_{}_ref.tif'.format(out, ascene.meta.id, band_id), 1)
        # res = myplanet.get_reflectance(bandpath_in, band_id, bandpath_out, ascene.meta, dt = 7, compress=None, overwrite=True)
        # if res:
            # print('File saved: {}'.format(bandpath_out))
        # bandpaths.append(bandpath_out)
        pass

    path2export = fullpath(out, ascene.meta.name(r'RF4-[fullsat]-[date]-[location]-[lvl].tif'))

    geodata.raster2raster(refpaths, path2export, path2target=None, method=geodata.gdal.GRA_NearestNeighbour, exclude_nodata=True, enforce_nodata=None, compress='LZW', overwrite=True)

    # ascene.calculate_index('NDVI', out)

    path2ndvi = r'{}\{}'.format(out, ascene.meta.name('NDVI-[fullsat]-[date]-[location]-[lvl].tif'))
    geodata.index_calculator.get('Normalized')([refpaths[3], refpaths[0]], path2ndvi)

    path2ndvi0 = r'{}\{}'.format(out, ascene.meta.name('NDVI0-[fullsat]-[date]-[location]-[lvl].tif'))
    geodata.index_calculator.get('Normalized')([ascene.get_band_path('nir'), ascene.get_band_path('red')], path2ndvi0)

    # path2shp = r'{}\{}'.format(out, ascene.meta.name('MWT-[fullsat]-[date]-[location]-[lvl].shp'))

    # geodata.save_to_shp(path2ndwi, path2shp, dst_fieldname=None, classify_table=[[None, 0, 1]], export_values=[1], overwrite=True)

def RGBNref(ascene):
    refpaths = []
    for band_id in ['red', 'green', 'blue', 'nir']:
        refpaths.append(ascene.get_product_path('Reflectance', band_id, set_product_path=out, set_name='{}-[fullsat]-[date]-[location]-[lvl].tif'.format(band_id.upper())))
    path2export = fullpath(out, ascene.meta.name(r'RF4-[fullsat]-[date]-[location]-[lvl].tif'))
    geodata.raster2raster(refpaths, path2export, path2target=None, method=geodata.gdal.GRA_NearestNeighbour, exclude_nodata=True, enforce_nodata=None, compress='LZW', overwrite=True)
    return None