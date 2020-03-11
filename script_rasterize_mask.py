# -*- coding: utf-8 -*-

from image_processor import *

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

path_in = folder_paths(r'e:\temp\image')[1]

path_vector_masks = {
    'PLN1001-20190429': r'e:\temp\masks\MWT-PLN-1001-20190429-3B_mask1_corrected.shp',
    'PLN1025-20190429': r'e:\temp\masks\MWT-PLN1025_0f02-20190429-3B_mask2_corrected.shp',
    'PLN0f02-20190429': r'e:\temp\masks\MWT-PLN1025_0f02-20190429-3B_mask2_corrected.shp',
    'PLN1008-20190428': r'E:/temp/masks/MWT-PLN10008-20190428-3B_mask3_corrected.shp'
}

folder_out = r'e:\temp\raster_masks'

if os.path.exists(folder_out) == False:
    os.makedirs(folder_out)

for key in path_vector_masks:

    for path in path_in:

        sat, date = key.split('-')

        if (sat in path) and (date in path):

            folder_in, file_in = os.path.split(path)
            path_out = fullpath(folder_out, file_in.replace('IM4', 'MWT'))
            geodata.RasterizeVector(path_vector_masks[key], path, path_out,
                                    value_colname=raster_index_col_name,
                                    filter_nodata=True,
                                    compress=compression,
                                    overwrite=overwrite_existing_files)
            print('Mask written: {}'.format(path_out))




