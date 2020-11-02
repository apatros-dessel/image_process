# -*- coding: utf-8 -*-

''' СОЗДАНИЕ РАЗМЕТКИ ДЛЯ НЕЙРОСЕТИ '''

from geodata import *
from shutil import copyfile

overwrite =  False          # Заменять существующие файлы
compression = 'DEFLATE'     # Алгоритм сжатия растровых данных
raster_id_col ='image'      # Название векторного поля, содержащего id растра
obj_index_col = 'gridcode'  # Название векторного поля, содержащего id объекта
mask_id = 'MFT'             # Индекс маски
mask_name = 'forests'       # Название папки с масками

data_folder = r'd:\terratech\neuro\urban_development'
path_out = r'e:\test\razmetka\data\pms_urban_development_tatarstan'
aux_img_folder = r'd:\terratech\kanopus_pms\tatarstan'

imsys_dict = {
    'kanopus': '^KV.*.L2$',
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

# Return files filtered by template
def collect_scenes(folder, template, raster_ext='tif', vector_ext='shp', pms=False, aux_img_paths=None):
    source_dict = OrderedDict()
    for path in folder_paths(folder, 1):
        f, id, ext = split3(path)
        id += '.L2'
        if (ext in (raster_ext, vector_ext)) and (re.search(template, id)):
            if pms:
                id = id.replace('.MS', '.PMS')
                if (ext==raster_ext) and aux_img_paths:
                    for aux_path in aux_img_paths:
                        aux_f, aux_id, aux_ext = split3(aux_path)
                        if id == aux_id:
                            path = aux_path
                            break
            if id in source_dict:
                source_dict[id][ext] = path
            else:
                source_dict[id] = {ext: path}
    return source_dict

# Make Kanopus neuro id
def kanopus_neuroid(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    type = dotsplit[2]
    lvl = dotsplit[3]
    scn_num = scn.replace('SCN', '')
    neuroid = '{}-{}-{}{}{}-{}'.format(satid, date, loc1, loc2, scn_num, lvl)
    if type == 'PMS':
        neuroid += 'PMS'
    return neuroid

for imsys in imsys_dict:

    template = imsys_dict[imsys]
    aux_img_paths = folder_paths(aux_img_folder, 1, 'tif')
    source_dict = collect_scenes(data_folder, template, pms=True, aux_img_paths=aux_img_paths)
    scroll(source_dict)

    if source_dict:

        img_folder = r'%s\\images\\%s' % (path_out, imsys)
        suredir(img_folder)
        mask_folder = r'%s\\masks\\%s\\%s' % (path_out, mask_name, imsys)
        suredir(mask_folder)

        for id in source_dict:

            img_path = source_dict[id].get('tif')
            vec_path = source_dict[id].get('shp')
            if None in (img_path, vec_path):
                continue
            neuro_id = kanopus_neuroid(id)

            copyfile(img_path, r'%s\\IM4-%s.tif' % (img_folder, neuro_id))

            RasterizeVector(vec_path, img_path, r'%s\\%s-%s.tif' % (mask_folder, mask_id, neuro_id),
                            value_colname=obj_index_col, compress=compression, overwrite=overwrite)

            print('Mask written: %s' % neuro_id)
