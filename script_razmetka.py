# -*- coding: utf-8 -*-

from image_processor import *

datapath_dict = OrderedDict()

# Далее для каждого типа объектов прописываются пути к месту хранения данных
# Если все исходные данные лежат в одной корневой папке, то достаточно указать путь к ней (как ниже с 'forests'); если таких папок много, можно записать их в список (как с 'mines')

save_rgbn_composites =      True   # Save RGBN composites from the original data
save_rgbn_reflectance =     True    # Save RGBN reflectance data
save_data_masks =           True   # Save raster object mask if a vector file is available
overwrite_existing_files =  False   # Replace existing files
compression =               'DEFLATE'  # Compression algorithm for raster (string)
raster_scene_id_col_name =  'image'
raster_data_path_col_name = 'RGBNpath'

# datapath_dict['forests'] = r''

datapath_dict['mines'] = [
                             r'f:\rks\tver',
                             # r'f:\rks\tver\20190911\20190911_062629_100d',
                             # r'f:\rks\digital_earth\kanopus\tver_source\KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2.DC.xml',
                           ]

path_to_razmetka = r'e:\test\razmetka'

dtype_id = {
    'PLN': 'planet',
    'KAN': 'kanopus',
}

obj_mask_dict = {
    'mines':        'MQR',
    'wastes':       'MWS',
    'water':        'MWT',
    'roads':        'MRD',
    'buildings':    'MBD',
    'construction': 'MCN',
    'materials':    'MMT',
    'technics':     'MTC',
    'ground':       'MGR',
    'forests':      'MFS',
    'fires':        'MFR',
}

vector_mask_dict = {
    # 'forests':  r'',
    'mines':    r'D:/digital_earth/data_2_razmetka/20200219/TVER_QUARRY_PLN_20200214.shp',
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

if save_data_masks:
    path_to_masks = fullpath(path_to_razmetka, 'masks')
    if os.path.exists(path_to_masks) == False:
        os.makedirs(path_to_masks)

for obj_id in datapath_dict:

    path_to_source_data = datapath_dict.get(obj_id)

    if path_to_source_data is None:
        continue

    save_data = {}

    for imsys in dtype_id:

        proc = process()
        proc.input(path_to_source_data, imsys_list=[imsys])

        if len(proc) == 0:
            continue

        if save_data_masks:
            vector_mask_path = vector_mask_dict.get(obj_id)
            if vector_mask_path is not None:
                if os.path.exists(vector_mask_path):

                    ds_in, lyr_in = geodata.get_lyr_by_path(vector_mask_path, 1)
                    if lyr_in is None:
                        continue
                    lyr_in.CreateField(geodata.ogr.FieldDefn(raster_data_path_col_name, 4))

                    for feat in lyr_in:
                        scene_id = str(feat.GetField(feat.GetFieldIndex(raster_scene_id_col_name)))
                        if scene_id is None:
                            print('Error collecting scene_id')
                        else:
                            for ascene in proc.scenes:
                                if scene_id in ascene.meta.id:
                                    data_path = r'{}\{}\{}'.format(path_to_data, dtype_id.get(imsys), ascene.meta.name('IM4-[fullsat]-[date]-[location]-[lvl].tif'))
                                    if scene_id not in save_data:
                                        save_data[scene_id] = ascene.fullpath
                                    feat.SetField(raster_data_path_col_name, data_path)
                                    break

                    path_to_mask_folder = r'{}\{}\{}'.format(path_to_masks, obj_id, dtype_id.get(imsys))
                    if os.path.exists(path_to_mask_folder) == False:
                        os.makedirs(path_to_mask_folder)

                    for scene_id in save_data:
                        ascene = scene(save_data[scene_id], imsys)
                        mask_name = ascene.meta.name('<obj_id>-[fullsat]-[date]-[location]-[lvl].tif').replace('<obj_id>', obj_mask_dict[obj_id])
                        path_to_mask = fullpath(path_to_mask_folder, mask_name)
                        raster_path = ascene.get_raster_path(ascene.meta.files[0])
                        vector_scene_mask_path = geodata.filter_dataset_by_col(vector_mask_path, raster_scene_id_col_name, scene_id)
                        geodata.RasterizeVector(vector_scene_mask_path, raster_path, path_to_mask, compress=compression, overwrite=overwrite_existing_files)
                        print('Mask written: {}'.format(path_to_mask))

        if save_rgbn_composites:
            path_to_rgbn_folder = r'{}\{}'.format(path_to_data, dtype_id.get(imsys))
            if os.path.exists(path_to_rgbn_folder) == False:
                os.makedirs(path_to_rgbn_folder)
            for scene_id in save_data:
                ascene = scene(save_data[scene_id], imsys)
                print(ascene.meta.lvl)
                rgbn_name = ascene.meta.name('IM4-[fullsat]-[date]-[location]-[lvl].tif')
                path_to_rgbn = fullpath(path_to_rgbn_folder, rgbn_name)
                res = ascene.default_composite('RGBN', path_to_rgbn, compress=compression, overwrite=overwrite_existing_files)
                if res==0:
                    print('RGBN written: {}'.format(path_to_rgbn))
                if save_rgbn_reflectance:
                    res = RGBNref(ascene, path_to_rgbn_folder)
                    if res == 0:
                        print('RGBN reflectance written: {}'.format('RF4'+rgbn_name[3:]))



