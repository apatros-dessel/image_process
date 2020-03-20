# -*- coding: utf-8 -*-

from image_processor import *
from shutil import copyfile

''' РАСТЕРИЗАЦИЯ ВЕКТОРНЫХ МАСОК НА ОСНОВЕ РАСТРОВЫХ ФАЙЛОВ '''

datapath_dict = OrderedDict()

# Далее для каждого типа объектов прописываются пути к месту хранения данных
# Если все исходные данные лежат в одной корневой папке, то достаточно указать путь к ней (как ниже с 'forests'); если таких папок много, можно записать их в список (как с 'mines')

overwrite_existing_files =  True   # Replace existing files
raster_scene_id_col_name =  'image_Plan' # Name for column with scene_ids
raster_index_col_name =     'gridcode'
compression =               'DEFLATE'  # Compression algorithm for raster (string)

path_in = [
    r'',
]

path_in = folder_paths(r'i:\forest_masks')[0][1:]

names_dict = xls_to_dict(r'e:\test\forest_masks\forest_masks_namedict.xls')

def kanopus_index(filename):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = undersplit = filename.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    type = dotsplit[2]
    # lvl = dotsplit[3]
    # ext = dotsplit[-1]
    scn_num = scn.replace('SCN', '')
    indexname = 'IM4-{}-{}-{}{}{}'.format(satid, date, loc1, loc2, scn_num)
    return indexname

def colfromdict(dict_, key, listed=False):
    col_dict = OrderedDict()
    for linekey in dict_:
        col_dict[linekey] = dict_[linekey].get(key)
    if listed:
        return col_dict.values()
    return col_dict

folder_in = r'J:\rks\kanopus_cherepan\Samara'
folder_out = r'e:\test\forest_masks'

if os.path.exists(folder_out) == False:
    os.makedirs(folder_out)

path_in = folder_paths(folder_in, files=True, extension='tif')
kanids = colfromdict(names_dict, 'kanopusid')
names_out = colfromdict(names_dict, 'filename')
vector_names = folder_paths(r'i:\forest_masks', files=True, extension='shp')
vector_ids = colfromdict(names_dict, 'oldid')

# scroll(path_in)
# scroll(kanids)
# scroll(names_out)

vec_paths = OrderedDict()

for vector_path in vector_names:
    for key_ in vector_ids:
        if vector_ids[key_] in vector_path:
            for path_ in folder_paths(os.path.split(vector_path)[0], files=True):
                vec_paths[key_] = vector_path
            break

# scroll(vec_paths)

for path in path_in:
    for key in kanids:
        if kanids[key] in path:
            # copyfile(path, os.path.join(folder_out, names_out[key]))
            path2raster = os.path.join(r'e:\test', names_out[key])
            # copyfile(path, path2raster)
            geodata.copydeflate(path, path2raster)
            basename_out = names_out[key].replace('IM4', 'MFS')[:-4]
            path2vector = vec_paths[key]
            print(path2raster)
            path_out = fullpath(r'e:\test', basename_out, 'tif')
            geodata.RasterizeVector(path2vector, path2raster, path_out,
                                    value_colname=raster_index_col_name,
                                    filter_nodata=True,
                                    compress=compression,
                                    overwrite=overwrite_existing_files)
            kanids.pop(key)
            break

scroll(kanids)

'''
for folder in path_in:
    path2raster = folder_paths(folder, files=True, extension='tif')[0]
    path2vector = folder_paths(folder, files=True, extension='shp')[0]
    file_in = os.path.split(path2raster)[1]
    file_basename = os.path.basename(path2vector)[:-4]
    for line in names_dict.values():
        if file_basename == line.get('oldid'):
            file_in = kanopus_index(line.get('newid'))+'-L2'
            print(file_in)
            copyfile(path2raster, fullpath(folder_out, file_in, 'tif'))
            file_out = file_in.replace('IM4', 'MFS')
            for ext in ['shp', 'shx', 'dbf', 'prj', 'cpg', 'xml']:
                try:
                    copyfile(path2vector, fullpath(folder_out, file_out, ext))
                except:
                    pass
    path_out = fullpath(folder_out, file_out, 'tif')
    geodata.RasterizeVector(path2vector, path2raster, path_out,
                            value_colname=raster_index_col_name,
                            filter_nodata=True,
                            compress=compression,
                            overwrite=overwrite_existing_files)
    print('Mask written: {}'.format(path_out))

for key in path_vector_masks:

    for path in path_in:

        sat, date = key.split('-')

        if (sat in path) and (date in path):

            folder_in, file_in = os.path.split(path)
            path_out = fullpath(folder_out, file_in.replace('IM4', 'MFS'))
            geodata.RasterizeVector(path_vector_masks[key], path, path_out,
                                    value_colname=raster_index_col_name,
                                    filter_nodata=True,
                                    compress=compression,
                                    overwrite=overwrite_existing_files)
            print('Mask written: {}'.format(path_out))




'''
pass