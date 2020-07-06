# -*- coding: utf-8 -*-

from image_processor import *
from shutil import copyfile

''' РАСТЕРИЗАЦИЯ ВЕКТОРНЫХ МАСОК НА ОСНОВЕ РАСТРОВЫХ ФАЙЛОВ '''

datapath_dict = OrderedDict()

# Далее для каждого типа объектов прописываются пути к месту хранения данных
# Если все исходные данные лежат в одной корневой папке, то достаточно указать путь к ней (как ниже с 'forests'); если таких папок много, можно записать их в список (как с 'mines')

overwrite_existing_files =  False   # Replace existing files
raster_scene_id_col_name =  'image' # Name for column with scene_ids
raster_index_col_name =     'gridcode'
compression =               'DEFLATE'  # Compression algorithm for raster (string)

def kanopus_index(filename):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = undersplit = filename.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    # type = dotsplit[2]
    # lvl = dotsplit[3]
    # ext = dotsplit[-1]
    scn_num = scn.replace('SCN', '')
    indexname = 'IM4-{}-{}-{}{}{}-L2'.format(satid, date, loc1, loc2, scn_num)
    return indexname

def colfromdict(dict_, key, listed=False):
    col_dict = OrderedDict()
    for linekey in dict_:
        col_dict[linekey] = dict_[linekey].get(key)
    if listed:
        return col_dict.values()
    return col_dict
'''
folder_in = r'J:\rks\kanopus_cherepan\Samara'
folder_out = r'e:\test\forest_masks'

if os.path.exists(folder_out) == False:
    os.makedirs(folder_out)

path_in = folder_paths(folder_in, files=True, extension='tif')
kanids = colfromdict(names_dict, 'kanopusid')
names_out = colfromdict(names_dict, 'filename')
vector_names = folder_paths(r'i:\forest_masks', files=True, extension='shp')
vector_ids = colfromdict(names_dict, 'oldid')
'''
# scroll(path_in)
# scroll(kanids)
# scroll(names_out)

raster_paths = [
    r'D:\terratech\changes_mask\IM4-S2B-20180423_20190428_T36VXK__mask1.tif',
    r'D:\terratech\changes_mask\IM4-S2B-20180503_20190428_Е36VXJ__mask2.tif',
    r'D:\terratech\changes_mask\IM4-S2B-20180503_20190430_T36VXH__mask3.tif',
]

vector_paths = [
    r'D:\terratech\changes_mask\MCHD-S2B-20190428-T36VXK_mask1_2020-03-16_mod.shp',
    r'D:\terratech\changes_mask\MCHD-S2B-20190430-Е36VXJ_mask2_2020-03-16_mod.shp',
    r'D:\terratech\changes_mask\MCHD-S2A-20190430-T36VXH_mask3_2020-03-16_mod.shp',
]

'''
for raster_path, vector_path in zip(raster_paths, vector_paths):

    path_out = raster_path.replace('.tif', '_mask.tif')
    geodata.RasterizeVector(vector_path, raster_path, path_out,
                            value_colname=raster_index_col_name,
                            filter_nodata=True,
                            compress=compression,
                            overwrite=overwrite_existing_files)

    folder, raster_name = os.path.split(raster_path)

    print(raster_name)

    maskid, sat, ending = raster_name.split('-')
    start, fin, tile, zero, ending = ending.split('_')
    mask = ending[:5]

    path_1 = [
        (raster_path, 3),
        (raster_path, 2),
        (raster_path, 1),
        (raster_path, 4),
    ]

    path_2 = [
        (raster_path, 7),
        (raster_path, 6),
        (raster_path, 5),
        (raster_path, 8),
    ]

    path_new = [
        (raster_path, 3),
        (raster_path, 2),
        (raster_path, 1),
        (raster_path, 4),
        (raster_path, 7),
        (raster_path, 6),
        (raster_path, 5),
        (raster_path, 8),

    ]

    path_tcp = [
        (raster_path, 7),
        (raster_path, 3),
        (raster_path, 6),
    ]

    name_1 = '-'.join(['IM4', sat, start, tile, 'L2_%s.tif' % mask])
    name_2 = '-'.join(['IM4', sat, fin, tile, 'L2_%s.tif' % mask])
    name_new = '_'.join(['MCHD', sat, start, tile, 'L2_%s' % mask, sat, fin, tile, 'L2_%s.tif' % mask])
    name_tcp = '_'.join(['TC3', sat, start, tile, 'L2', sat, fin, tile, 'L2.tif'])

    # geodata.raster2raster(path_1, fullpath(folder, name_1), compress='DEFLATE', overwrite=True)
    # geodata.raster2raster(path_2, fullpath(folder, name_2), compress='DEFLATE', overwrite=True)
    # geodata.raster2raster(path_new, fullpath(folder, name_new), compress='DEFLATE', overwrite=True)
    geodata.raster2raster(path_tcp, fullpath(folder, name_tcp), compress='DEFLATE', overwrite=True)

'''

# path_in = r'd:\terratech\Les_Kanopus\image\Tatarstan'
path_shp = r'g:\rks\digital_earth\data_2_razmetka\20200423\Tatarstan\TATARSTAN_QUARRY_KAN_20200422_epsg32639.shp'
path_pms = r'g:\rks\digital_earth\processed\kanopus\Tatarstan\ms'
path_out = r'd:\terratech\razmetka\set010__20200424__tatarstan_mines_kanopus_ms'

path_im4 = fullpath(path_out, r'images\kanopus')
path_mfr = fullpath(path_out, r'masks\mines\kanopus')

suredir(path_im4)
suredir(path_mfr)

filepath_list = folder_paths(path_pms, files=True, extension='tif')
# shppath_list = folder_paths(path_shp, files=True, extension='shp')
pmspath_list = folder_paths(path_pms, files=True, extension='tif')

j = 1
for i, filepath in enumerate(filepath_list):

    folder, file = os.path.split(filepath)
    kan_nameIM4 = kanopus_index(file)#.replace('.MS', '.PMS')
    kan_nameMSK = kan_nameIM4.replace('IM4', 'MQR')
    temp_shp = tempname('shp')
    print(file[:-4].replace('.MS', '.PMS'))
    geodata.filter_dataset_by_col(path_shp, raster_scene_id_col_name, file[:-4].replace('.MS', '.PMS'), path_out=temp_shp)
    filter_ds, filter_lyr = geodata.get_lyr_by_path(temp_shp)
    if filter_lyr is not None:
        if filter_lyr.GetFeatureCount() > 0:
            # print(temp_shp)
            geodata.RasterizeVector(temp_shp, filepath, fullpath(path_mfr, kan_nameMSK, 'tif'),
                                    value_colname=raster_index_col_name,
                                    filter_nodata=True,
                                    compress=compression,
                                    overwrite=overwrite_existing_files)
            copyfile(filepath, fullpath(path_im4, kan_nameIM4, 'tif'))
            # print('%i Mask written: %s' % (j, kan_nameIM4))
            j +=1
            continue
    # print('%i Error writing mask: %s' % (i+1, kan_nameIM4))

# scroll(filepath_list)
