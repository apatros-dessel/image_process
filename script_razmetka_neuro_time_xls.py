# -*- coding: utf-8 -*-

''' СОЗДАНИЕ РАЗМЕТКИ ДЛЯ НЕЙРОСЕТИ '''

from geodata import *

overwrite =  False          # Заменять существующие файлы
compression = 'DEFLATE'     # Алгоритм сжатия растровых данных
raster_id_col ='image'      # Название векторного поля, содержащего id растра
obj_index_col = 'gridcode'  # Название векторного поля, содержащего id объекта
mask_id = 'MFT'             # Индекс маски
mask_name = 'forests'       # Название папки с масками

path_xls = r'D:\terratech\change_detection\image_table.xls'
path_out = r'e:\test\razmetka_change'

xls_dict = xls_to_dict(path_xls)

for id in xls_dict:

    meta = xls_dict[id]

    # scroll(meta)

    folder = meta.get('folder')
    date1 = meta.get('date1')
    date2 = meta.get('date2')
    image = meta.get('image')
    vector = meta.get('vector')
    neuroid = meta.get('pair_neuroid')
    bands = meta.get('bands')

    if None in (folder, date1, date2, image, vector, neuroid, bands):
        print('%s Error extracting data' % id)
        continue
    bands = flist(bands.decode().split(','), int)
    img_path = fullpath(folder, image)
    # vec_path = fullpath(folder, vector)
    vec_path = vector

    for p in (img_path, vec_path):
        stop = False
        if not os.path.exists(p):
            print('File not found: %s' % p)
            stop = True
            break
    if stop:
        continue

    suredir(path_out)

    try:
        SaveRasterBands(img_path, bands, r'%s\IMCH8_%s.tif' % (path_out, neuroid),
                    options={'compress': 'DEFLATE'}, overwrite=overwrite)

        RasterizeVector(vec_path, img_path, r'%s\MCHD_%s.tif' % (path_out, neuroid),
                    value_colname=obj_index_col, compress=compression, overwrite=overwrite)

        print('Change written: %s' % neuroid)

    except:

        print('Error witing: %s' % neuroid)