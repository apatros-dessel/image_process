# -*- coding: utf-8 -*-

from image_processor import *

datapath_dict = OrderedDict()

# Далее для каждого типа объектов прописываются пути к месту хранения данных
# Если все исходные данные лежат в одной корневой папке, то достаточно указать путь к ней (как ниже с 'forests'); если таких папок много, можно записать их в список (как с 'mines')

save_rgbn_composites =      True   # Save RGBN composites from the original data
# save_rgbn_reflectance =     False    # Save RGBN reflectance data
# save_data_masks =           True   # Save raster object mask if a vector file is available
overwrite_existing_files =  False   # Replace existing files
compression =               'DEFLATE'  # Compression algorithm for raster (string)
# raster_scene_id_col_name =  'image'
# raster_data_path_col_name = 'RGBNpath'
# raster_index_col_name =     'gridcode'

# datapath_dict['forests'] = r''

path = r''
path2filter = r'c:\Users\Home\Desktop\16b939d26071a2c2.txt'

if os.path.exists(path2filter):
    if path2filter.endswith('.xls'):
        xls_dict = xls_to_dict(path2filter)
        path_to_source_data = []
        for rowkey in xls_dict:
            path_to_source_data.append(xls_dict[rowkey].get('fullpath', '').encode('utf-8'))
    elif path2filter.endswith('.txt'):
        path_to_source_data = []
        proc0 - process().input(path0)
        ids - proc0.getids()
        with open(path2filter) as txt:
            lines = txt.read().split('\n')
            for line in lines:
                if line in ids:
                    path_to_source_data.append(proc0.get_scene(line).folder)

path_to_razmetka = r'e:\test\razmetka'

dtype_id = {
    'PLN': 'planet',
    'KAN': 'kanopus',
}

if path_to_razmetka.endswith('data') == False:
    path_to_razmetka = r'{}\data'.format(path_to_razmetka)

if os.path.exists(path_to_razmetka) == False:
    os.makedirs(path_to_razmetka)

razmetka_folders = os.walk(path_to_razmetka).next()[1]
cur_date = str(datetime.now().date()).replace('-','')

current_folder = 'set{}_{}'.format(len(razmetka_folders)+1, cur_date)
for folder in razmetka_folders:
    if re.search(cur_date, folder) is not None:
        current_folder = folder
path_to_razmetka = fullpath(path_to_razmetka, current_folder)
if os.path.exists(path_to_razmetka) == False:
    os.makedirs(path_to_razmetka)

if save_rgbn_composites:
    path_to_data = fullpath(path_to_razmetka, 'images')
    if os.path.exists(path_to_data) == False:
        os.makedirs(path_to_data)

for imsys in dtype_id:

    proc = process()
    proc.input(path_to_source_data, imsys_list=[imsys])

    if len(proc) == 0:
        continue

    if save_empty_masks:
        path_to_empty_masks = r'{}\masks\water\{}'
        suredir(path_to_empty_masks)

    if save_rgbn_composites:
        path_to_rgbn_folder = r'{}\{}'.format(path_to_data, dtype_id.get(imsys))
        path_to_empty_masks = r'{}\masks\water\{}'
        for dir in (path_to_rgbn_folder, path_to_empty_masks):
            suredir(dir)
        for ascene in proc.scenes:
            # ascene = scene(save_data[scene_id], imsys)
            # print(ascene.meta.lvl)
            rgbn_name = ascene.meta.name('IM4-[fullsat]-[date]-[location]-[lvl].tif')
            path_to_rgbn = fullpath(path_to_rgbn_folder, rgbn_name)
            res = ascene.default_composite('RGBN', path_to_rgbn, compress=compression, overwrite=overwrite_existing_files)
            if res==0:
                print('RGBN written: {}'.format(path_to_rgbn))
            # else:
                # print('Error saving RGBN: {}'.format(path_to_rgbn))
            nullmask_name = ascene.meta.name('MQR-[fullsat]-[date]-[location]-[lvl].tif')
            path_to_nullmask = fullpath(path_to_empty_masks, nullmask_name)
            ds(path_to_nullmask, copypath = path_to_rgbn, options = {'bandnum': 1, 'dt': 1, 'compress': 'DEFLATE'},
               overwrite=overwrite_existing_files)



