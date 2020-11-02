# -*- coding: utf-8 -*-

''' СОЗДАНИЕ РАЗМЕТКИ ДЛЯ НЕЙРОСЕТИ '''

from geodata import *

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
    'sentinel': '^S2.*SAFE$',
}

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Sentinel-2 name
def parse_sentinel(id):
    # S2A_MSIL2A_20160806T085602_N0213_R007_T36VVH_20200326T125942.SAFE.tif
    satid, typelvl, datetime, base, orbit, tile, ending = id.split('_')
    type = typelvl[:3]
    lvl = typelvl[3:]
    date = datetime.split('T')[0]
    time = datetime.split('T')[1]
    date2 = ending.split('T')[0]
    time2 = ending.split('T')[1].split('.')[0]
    return satid, type, lvl, date, time, base, orbit, tile, date2, time2

def get_neuroid(id):
    if id.startswith('KV'):
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[4:]
        if type=='PMS':
            lvl += type
    elif id.startswith('S2'):
        satid, type, lvl, date, time, base, orbit, tile, date2, time2 = parse_sentinel(id)
        loc = tile
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = '%s-%s-%s-%s' % (satid, date, loc, lvl)
    return neuroid

def get_neouroid_time(id1, id2):
    return '%s_%s' % (get_neuroid(id1), get_neuroid(id2))

# Find source scenes and dates
def get_img_dict(folder):
    img_dict = OrderedDict()
    for name in os.listdir(folder):
        if os.path.isfile(fullpath(folder, name)):
            id, ext = os.path.splitext(name)
            if ext.lower()=='.tif':
                for imsys in globals()['imsys_dict']:
                    tmpt = imsys_dict[imsys]
                    if re.search(tmpt, id):
                        if imsys=='kanopus':
                            satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
                        elif imsys=='sentinel':
                            satid, type, lvl, date, time, base, orbit, tile, date2, time2 = parse_sentinel(id)
                        img_dict[date] = name
    return img_dict

# Find time folders for time change masks
def get_time_folders(folder):
    folders = []
    tmpt = '^\d{8}$'
    for name in os.listdir(folder):
        path = fullpath(folder, name)
        if os.path.isdir(path):
            time_name_list = name.split('_')
            if len(time_name_list)>2:
                t0 = time_name_list[0]
                t1 = time_name_list[1]
                chid = '_'.join(time_name_list[2:])
                if re.search(tmpt, t0) and re.search(tmpt, t1):
                    folder_dict = OrderedDict()
                    folder_dict['t0'] = t0
                    folder_dict['t1'] = t1
                    folder_dict['id'] = chid
                    folder_dict['path'] = path
                    folders.append(folder_dict)
    return folders

def get_vector_names(folder):
    names = []
    tmpt = '^\d{8}$'
    for name in os.listdir(folder):
        if os.path.isfile(fullpath(folder, name)):
            shpid, ext = os.path.splitext(name)
            if ext.lower()=='.shp':
                time_name_list = shpid.split('_')
                if (len(time_name_list)>3) and (time_name_list[0]=='changes'):
                    t1 = time_name_list[1]
                    t2 = time_name_list[2]
                    chid = '_'.join(time_name_list[3:])
                    if re.search(tmpt, t1) and re.search(tmpt, t2):
                        folder_dict = OrderedDict()
                        folder_dict['t1'] = t1
                        folder_dict['t2'] = t2
                        folder_dict['id'] = chid
                        folder_dict['name'] = name
                        names.append(folder_dict)
    return names

def get_composits(folder, timeid):
    for path in folder_paths(folder, 1, 'tif'):
        f, name, ext = split3(path)
        if name.startswith(timeid):
            return path

# Find bands nums according to image types
def find_bands_list(id1, id2):
    if id1.startswith('S2'):
        return (1,2,3,4,5,6,7,8)
    else:
        return (1,2,3,4,6,7,8,9)

def get_new_ids(folder):


def make_change_masks(folder, img_folder, mask_folder):

    img_dict = get_img_dict(folder)
    vec_names = get_vector_names(folder)

    for vec_dict in vec_names:

        t1 = vec_dict.get('t1')
        t2 = vec_dict.get('t2')
        id1 = img_dict.get(t1)
        id2 = img_dict.get(t2)

        if not None in (id1, id2):

            id1 = os.path.splitext(id1)[0]
            id2 = os.path.splitext(id2)[0]

            print(id1, id2)

            vec_path = fullpath(folder, vec_dict.get('name'))
            neuroid = get_neouroid_time(id1, id2)
            bands_list = find_bands_list(id1, id2)
            raster_path = get_composits(folder, '%s_%s' % (t1, t2))
            suredir(img_folder)
            suredir(mask_folder)

            SaveRasterBands(raster_path, bands_list, r'%s\IMCH8_%s.tif' % (img_folder, neuroid),
                            compress=compression, overwrite=overwrite)

            RasterizeVector(vec_path, raster_path, r'%s\MCHD_%s.tif' % (mask_folder, neuroid),
                            value_colname=obj_index_col, compress=compression, overwrite=overwrite)

            print('Change written: %s' % neuroid)

folder = r'd:\terratech\change_detection\new_mask\aoi2'
img_folder = r'E:\test\neurotime'
mask_folder = r'E:\test\neurotime'

make_change_masks(folder, img_folder, mask_folder)
