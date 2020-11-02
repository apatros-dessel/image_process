from image_processor import *
from shutil import copyfile

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

# path2oldband = [(r'e:\test\newsnt\S2A_MSIL1C_20150822_NDVI_DOS1.tif', 1)]
# path2newband = [(r'e:\test\newsnt\S2B_MSIL1C_20180801_NDVI_DOS1.tif', 1)]
path2oldband = (r'e:\test\newsnt\S2B_MSIL1C_20180801_NDVI_DOS1.tif', 1)
path2newband = (r'e:\test\newsnt\S2A_MSIL2A_20190828_NDVI_DOS1.tif', 1)
min_path = r'e:\test\test_minus.tif'
# quot_path = r'e:\test\test_quot.tif'
class_path = r'e:\test\test_class.tif'
path2shp = r'e:\test\test_change.shp'

# geodata.band_difference(path2oldband, path2newband, min_path, nodata = 0, compress = None, overwrite = True)
# geodata.band_quot(path2oldband, path2newband, quot_path, nodata = 0, compress = None, overwrite = True)

# geodata.ClassifyBandValues((min_path, 1), (class_path, 3), classify_table = [(None, -0.1, -1), (0.1, None, 1)], nodata = 0, compress = 'LZW', overwrite = True)
# geodata.ClassifyBandValues(path2oldband, (class_path, 2), classify_table = [(0, 0.1, 1), (0.1, 0.5, 2), (0.5, 0.6, 3), (0.6, 0.7, 4), (0.7, 0.8, 5), (0.8, 1, 10)], nodata = 0, compress = 'LZW', overwrite = True)
# geodata.ClassifyBandValues(path2newband, (class_path, 1), classify_table = [(0, 0.1, 1), (0.1, 0.5, 2), (0.5, 0.6, 3), (0.6, 0.7, 4), (0.7, 0.8, 5), (0.8, 1, 10)], nodata = 0, compress = 'LZW', overwrite = True)


# geodata.save_to_shp(min_path, path2shp, band_num = 1, classify_table = [[None, -0.1, -1], [0.1, None, 1]], export_values = None, overwrite = True)
# geodata.VectorizeBand((min_path, 1), path2shp, classify_table = [[None, -0.1, -1], [0.1, None, 1]], erode_val=1, overwrite = True)

# geodata.Changes(path2oldband, path2newband, min_path, calc_path = None, formula = 0, lower_lims = None, upper_lims = None, check_all_values = False, upper_priority = True)

path2shp = r'd:\digital_earth\data_2_razmetka\other\20200221\TBO_tver_polygon_4326.shp'
column = ''
path_in = [
    r'f:\rks\tver',
]
path2rgb = r'e:\planet_rgb'
path_out = r'e:\planet_rgb_crop1'

folders = []
files = []

for path in path_in:
    new_folders, new_files = folder_paths(path)
    folders.extend(new_folders)
    files.extend(new_files)

shp_ds, shp_lyr = geodata.get_lyr_by_path(path2shp)

if shp_lyr is None:
    raise Exception('Cannot open file: {}'.format(path2shp))

export_files = []

proc = process()
proc.input(path_in)
covers_dict = proc.get_cover_paths()

# scroll(covers_dict)

export_id_list = []

for scene_id in covers_dict:
    scene_ds, scene_lyr = geodata.get_lyr_by_path(covers_dict[scene_id])
    # print(scene_lyr)
    for scene_feat in scene_lyr:
        scene_geom = scene_feat.GetGeometryRef()
        # print(scene_geom)
        shp_lyr.ResetReading()
        for feat in shp_lyr:
            if scene_geom.Intersect(feat.GetGeometryRef()):
                export_id_list.append(scene_id)

scroll(export_id_list)
print(len(export_id_list))

rgb_folders, rgb_files = folder_paths(path2rgb)

# print(len(rgb_files))

for ascene in proc.scenes:
    if ascene.meta.id in export_id_list:
        name_id = ascene.meta.name('[id]')
        print(name_id)
        for rgb_filepath in rgb_files:
            if name_id in rgb_filepath:
                export_files.append(rgb_filepath)

scroll(export_files)

'''
for feat in shp_lyr:
    scene_id = feat.GetField(feat.GetFieldIndex(column))
    error = True
    if scene_id is not None:
        for file in files:
            if scene_id in file:
                if file not in export_files:
                    export_files.append(file)
                error = False
                break
    if error:
        print('Scene_id not found: {}'.format(scene_id))
'''

print(len(export_files))

# for filepath in export_files:
    # copyfile(filepath, fullpath(path_out, os.path.split(filepath)[1]))
    # print('File saved: {}'.format(fullpath(path_out, os.path.split(filepath)[1])))