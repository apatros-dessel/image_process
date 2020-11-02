# -*- coding: utf-8 -*-
# Anything was grist that came to the Royal Navy’s mill!

from geodata import *

pin = [r'\\172.21.195.2\FTP-Share\ftp\landcover\prepare of mask\sbor_masok_Gari']                  # Путь к исходным файлам (растровым или растровым и векторным), можно указать список из нескольких директорий
vin = None     # Путь к векторному файлу масок (если None или '', то ведётся поиск векторных файлов в директории pin)
pout = r'e:\rks\razmetka\set038__gari_change'                  # Путь для сохранения конечных файлов
imgid = 'IMCH10'                   # Индекс изображений (управляет числом каналов в конечном растре)
maskid = u'изменения'                # Индекс масок (MWT, MFS и т.д.)
split_vector = False        # Если True, то исходный вектор разбивается по колонке image_col, в противном случае будут использованы маски для всех векторных объектов
image_col = 'path'              # Название колонки идентификатора растровой сцены (если vin != 0)
code_col = 'gridcode'               # Название колонки с кодовыми значениями
compress = 'DEFLATE'        # Алгоритм сжатия растровых данных
overwrite = False          # Заменять существующие файлы
pms = True                  # Использовать паншарпы
replace_vals = {44:144, 45:145}         # Изменить значения в конечной маске в соответствии со словарём, если None, то замены не производится

input_from_report = None  # Путь к таблице xls с путями к источникам данных, если None, то пары снимок-вектор строятся заново
# Менять источники можно вручную, формат xlsx не читает

vecids_path = None  # Список id при их отсутствии в исходном векторном файле. Если None, то поиск будет производиться в колонке image_col

source_paths = r'%s\image_processor\raster_paths.txt' % os.environ['TMP']                   # Путь к текстовому файлу с перечнем путей к доступным растровым файлам
# Файл включает список корневых директорий и список путей к файлам, разделённых пустой строкой ('\n\n')
# При отличии списка корневых директорий от pin файл будет перезаписан!

satellite_types = {
    'Sentinel': {'tmpt': r'S2[AB]', 'folder': 'sentinel'},
    'Kanopus': {'tmpt': r'KV[1-6I]', 'folder': 'kanopus'},
    'Resurs': {'tmpt': r'RP\d', 'folder': 'resurs'},
    'Planet': {'tmpt': r'PLN.+', 'folder': 'planet'},
}

composite_types = {
    'Sentinel-Sentinel': {'sources': ('Sentinel', 'Sentinel'), 'folder': 'sentinel_sentinel'},
    'Sentinel-Kanopus': {'sources': ('Sentinel', 'Kanopus'), 'folder': 'sentinel_kanopus'},
}

mask_types = {
    u'карьеры': {'id': 'MQR', 'folder': 'mines', },
    u'вода':    {'id': 'MWT', 'folder': 'water'},
    u'лес':     {'id': 'MFS', 'folder': 'forest'},
    u'изменения': {'id': 'MCHD', 'folder': 'change'},
    u'full':    {'id': 'MSK', 'folder': 'full'},
    u'свалки':  {'id': 'MWS', 'folder': 'svalki'},
    u'зарастание': {'id': 'MFG', 'folder': 'fields_grow'},
    u'дома':    {'id': 'MBD', 'folder': 'houses'},
    u'ТБО':     {'id': 'MWS', 'folder': 'wastes'},
    u'дороги':  {'id': 'MRD', 'folder': 'roads'},
    u'гари':    {'id': 'MFR', 'folder': 'gari'},
}

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl


# Parse Resurs name
def parse_resurs(id):
    satid, loc1, sentnum, geoton, date, num1, ending = id.split('_')
    ending = ending.split('.')
    if len(ending) == 4:
        num2, scn, type, lvl = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, ''
    elif len(ending) == 5:
        num2, scn, type, lvl, grn = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn
    else:
        raise Exception('Wrong ending length for %s' % id)


# Parse Sentinel name
def parse_sentinel(id):
    # S2B_MSIL1C_20190828T043709_N0208_R033_T48VUP_20190828T082130
    # S2A_MSIL1C_20190828_T37VCD # shortid for time composits
    vals = id.split('_')
    if len(vals) == 7:
        satid, lvl, datetime, col, row, tile, datetime2 = id.split('_')
        cutid = ''
    elif len(vals) == 8:
        satid, lvl, datetime, col, row, tile, datetime2, cutid = id.split('_')
        tile += cutid
    elif len(vals) == 4:
        satid, lvl, datetime, tile = id.split('_')
    else:
        return '', '', '', '', ''
    lvl = lvl[-3:]
    dt = datetime.split('T')
    if len(dt)==2:
        date, time = dt
    else:
        date = dt[0]
        time = ''
    return satid, date, time, tile, lvl

# Расширенная функция расчёта neuroid, учитывающая готовые neuroid и названия разновременных композитов
def neuroid_extended(id):
    if re.search(r'^IM\d+-.+-\d+-.+-.+$', id):
        return id
    elif re.search(r'IMCH\d+__.+__.+', id):
        vals = id.split('__')
        for i in (1, 2):
            part_neuroid = neuroid_extended(vals[i])
            vals[i] = part_neuroid[part_neuroid.index('-')+1:]
        return '__'.join(vals)
    else:
        return get_neuroid(id)

# Получить neuroid из исходного имени файла (для 4-х канального RGBN)
def get_neuroid(id):
    if re.search(r'^KV.+L2$', id):
        id = re.search(r'KV.+L2', id).group()
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[3:]
        if type == 'PMS':
            lvl += type
    # Ресурс-П обрабатывается только из гранул!
    elif re.search(r'^RP.+L2.GRN\d+$', id):
        id = re.search(r'RP.+L2.GRN\d+', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = parse_resurs(id)
        loc = loc1 + scn[3:] + grn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^S2[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel(id)
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = imgid+'-%s-%s-%s-%s' % (satid, date, loc, lvl)

    # IM4 в начале -- условность, его можно будет изменить на этапе обработки изображения, если в нём больше 4 каналов
    return neuroid


# Получить список значений колонки векторного файла
def get_col_keys(vec, colname):
    din, lin = get_lyr_by_path(vec)
    if lin is None:
        return None
    else:
        keys = []
        for feat in lin:
            key = feat.GetField(colname)
            if (key is not None) and (key not in keys):
                keys.append(key)
        return keys


# Обработать искажённые индексы растровых файлов с тем, чтобы получить правильное название растра
# Работает только в случае, когда нужно извлекать хитро выебанные названия файлов из атрибутов вектора
# Для временных композитов не сработает, проще заставить поставщика предоставить по одному векторному файлу на каждый растр
def filter_id(id, pms=False):
    for tmpt in (r'KV.+SCN\d+', r'IM\d+-.+-L2', r'IM\d+-.+\d{2,}', r'^S2.+\d+T\d+$', r'RP.+L2.GRN\d+'):
        search = re.search(tmpt, id)
        if search:
            report = search.group()
            # Для случая, когда вектор уже создан по переименованному растру
            # Найти растр с оригинальным именем по neuroid не выйдет -- предполагается, что если соответствующий растр есть у поставщика данных, то у нас будет и подавно
            if report.startswith('IM4'):
                if not report.endswith('-L2'):
                    report += '-L2'
                if pms:
                    report += 'PMS'
            # Редкая ошибка для переформатированных имён Канопусов
            elif report.startswith('KV'):
                report = report.replace('_SCN', '.SCN')
                if pms:
                    report += '.PMS.L2'
                else:
                    report += '.MS.L2'
                # report = get_neuroid(report)
            return report


def check_nonzeros(path):
    l = len(np.unique(gdal.Open(path),GetRasterBand(1).ReadAsArray()))
    print(l)
    return bool(l)


def get_raster_paths(raster_path):
    raster_path = obj2list(raster_path)
    pinstr = '\n'.join(pin)
    if os.path.exists(globals()['source_paths']):
        with open(globals()['source_paths']) as path_data:
            pin_, paths_ = path_data.read().split('\n\n')
            if pin_ == pinstr:
                return paths_.split('\n')
    export = []
    for folder in raster_path:
        export.extend(folder_paths(folder, 1, 'tif'))
    with open(globals()['source_paths'], 'w') as path_data:
        path_data.write('{}\n\n{}'.format(pinstr, '\n'.join(export)))
        print('Written source paths to: %s' % globals()['source_paths'])
    return export


# Checks if name must be excluded as pansharpened or not pansharpened
def pms_exit(id, pms = False):
    if re.search('KV.+SCN\d+.+', id):
        if id.endswith('PMS'):
            if not pms:
                return True
        else:
            if pms:
                return True
    return False


# Получить пути к исходным данным для масок для разделённых векторных файлов (shp, json, geojson) и растровых снимков (tif)
def get_pair_paths(pin, pms = False):
    export = OrderedDict()
    for folder in obj2list(pin):
        paths = folder_paths(folder, 1)
        for path in paths:
            f,n,e = split3(path)
            id = neuroid_extended(n)
            if id is None:
                continue
            if pms_exit(id, pms):
                continue
            if e == 'tif':
                if id in export:
                    export[id]['r'] = path
                else:
                    export[id] = {'r': path}
            elif e in ('shp', 'json', 'geojson'):
                if id in export:
                    export[id]['v'] = path
                else:
                    export[id] = {'v': path}
    for id in export:
        if ('v' in export[id]) and ('r' in export[id]):
            export[id]['pairing'] = True
        else:
            export[id]['pairing'] = False
    return export


# Получить пути к исходным данным для масок для цельных векторных файлов
def get_pairs(raster_paths, vin, img_colname, vecids=None, split_vector=True, pms=False):
    export = OrderedDict()
    if vecids is None:
        vecids = get_col_keys(vin, img_colname)
    raster_names = flist(raster_paths, lambda x: split3(x)[1])
    for vecid in vecids:
        id = filter_id(vecid, pms=pms)
        for i, rasterid in enumerate(raster_names):
            if id == rasterid:
                try:
                    neuroid = neuroid_extended(id)
                    if split_vector:
                        export[neuroid] = {'r': raster_paths[i], 'v': filter_dataset_by_col(vin, img_colname, vecid)}
                    else:
                        export[neuroid] = {'r': raster_paths[i], 'v': vin}
                    export[neuroid]['pairing'] = True
                except:
                    if not ('neuroid' in locals()):
                        neuroid = vecid
                    if neuroid:
                        if neuroid in export:
                            export[neuroid]['pairing'] = False
                        else:
                            export[neuroid] = {'pairing': False}
                finally:
                    print('%s pairing %s' % (('ERROR', 'SUCCESS')[bool(neuroid)], vecid))
                    break
    return export

# Получить полные пути к растрам в разметке (автоматически создаётся нужная директория)
def get_paths(pout, id, maskid, imgid):
    satellite_types = globals()['satellite_types']
    fail = True
    if re.search(r'IMCH\d+__.+__.+', id) and re.search('^IMCH\d+$', imgid):
        composite_types = globals()['composite_types']
        nameparts = id.split('__')
        name1, name2 = nameparts[1:3]
        for compid in composite_types:
            sat1 = satellite_types[composite_types[compid]['sources'][0]]['tmpt']
            sat2 = satellite_types[composite_types[compid]['sources'][1]]['tmpt']
            if re.search(sat1, name1.split('-')[0]) and re.search(sat2, name2.split('-')[0]):
                sat_folder = composite_types[compid]['folder']
                nameparts[0] = imgid
                imgname = '__'.join(nameparts)
                fail = False
                break
        if fail:
            print('Unknown time composite for %s')
            return None
    elif re.search(r'^IM\d+-.+-\d+-.+-.+$', id) and re.search('^IM\d+$', imgid):
        for satid in satellite_types:
            if re.search(satellite_types[satid]['tmpt'], id.split('-')[1]):
                sat_folder = satellite_types[satid]['folder']
                nameparts = id.split('-')
                nameparts[0] = imgid
                imgname = '-'.join(nameparts)
                fail = False
        if fail:
            print('Unknown satellite for: %s' % id)
            return None
    else:
        print('Wrong id format: %s' % id)
        return None
    img_folder = r'%s\images\%s' % (pout, sat_folder)
    msk_type = globals()['mask_types'].get(maskid)
    if msk_type:
        msk_folder = r'%s\masks\%s\%s' % (pout, msk_type['folder'], sat_folder)
    else:
        print('Unknown mask type: %s' % msk_type)
        return None
    for folder in (img_folder, msk_folder):
        suredir(folder)
    img_path = fullpath(img_folder, imgname, 'tif')
    if len(imgid) == 3:
        msk_path = fullpath(msk_folder, msk_type['id']+id[3:], 'tif')
    else:
        msk_path = fullpath(msk_folder, msk_type['id'] + id[4:], 'tif')
    return (img_path, msk_path)


# Check if the image needs repair
def check_image(img_in, neuro):
    raster = gdal.Open(img_in)
    realBandNum = raster.RasterCount
    img_type = neuro.split('__')[0].split('-')[0]
    if re.search(r'^IM\d+$', img_type):
        metaBandNum = int(img_type[2:])
    elif re.search(r'IMCH\d+$', img_type):
        metaBandNum = int(img_type[4:])
    counter = min((metaBandNum, realBandNum))
    if metaBandNum > realBandNum:
        print('Not enough bands for: %s - got %i, need %i' % (img_in, realBandNum, metaBandNum))
        raise Exception
    elif metaBandNum < realBandNum:
        print('Band count mismatch for: %s - got %i, need %i' % (img_in, realBandNum, metaBandNum))
        return True, counter
    counter = min((metaBandNum, realBandNum))
    for i in range(1, counter + 1):
        band = raster.GetRasterBand(i)
        if band.DataType != 3 or band.GetNoDataValue() != 0:
            return True, counter
    # print(counter)
    return False, counter


# Записать изображение, проверяя корректность его формата
# Если overwrite==False, то изображения в корректном формате пропускаются
def set_image(img_in, img_out, overwrite = False, band_reposition = None):
    if os.path.exists(img_out):
        repair, counter = check_image(img_out, split3(img_out)[1])
        if not (repair or overwrite):
            return img_out
    if os.path.exists(img_in):
        repair, counter = check_image(img_in, split3(img_out)[1])
    else:
        print('Path not found: %s' % img_in)
        return 'ERROR: Source file not found'
    if repair:
        return repair_img(img_in, img_out, counter, band_order = band_reposition)
    else:
        shutil.copyfile(img_in, img_out)
        return img_out

# Записать растр снимка в установленном формате
def repair_img(img_in, img_out, count, band_order=None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':3, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(band_order, range(1, count+1)):
        arr_ = raster.GetRasterBand(bin).ReadAsArray()
        o = np.unique(arr_)[0]
        arr_[arr_ == o] = 0
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out


# Создать растровую маску на основе вектора
def set_mask(img_in, vec_in, msk_out, overwrite=False):
    if check_exist(msk_out, ignore=overwrite):
        return msk_out
    crs = get_srs(gdal.Open(img_in))
    vec_reprojected = tempname('shp')
    vec_to_crs(ogr.Open(vec_in), crs, vec_reprojected)
    if not os.path.exists(vec_reprojected):
        vec_reprojected = vec_in
    try:
        RasterizeVector(vec_reprojected, img_out, msk_out, data_type=2,
                    value_colname=code_col, compress=compress, overwrite=overwrite)
        return msk_out
    except:
        print('Rasterizing error: %s %s' % (img_in, vec_in))
        return 'ERROR: Rasterizing error'


# Заменить значения в конечном растре, в соответствии со словарём
def replace_values(f, replace):
    raster = gdal.Open(f, 1)
    band = raster.GetRasterBand(1)
    arr_ = band.ReadAsArray()
    for key in replace:
        if key in arr_:
            arr_[arr_ == key] = replace[key]
    band.WriteArray(arr_)
    raster = None
    # print(split3(f)[1], list(np.unique(gdal.Open(f).ReadAsArray())))


def check_type(codes):
    type_dict = {a: 0 for a in mask_types}
    mines = list(range(1,4)) + list(range(10,14)) + list(range(20,24)) + list(range(26,27)) + list(range(30,34))
    for c in codes:
        if c in mines:
            type_dict[u"карьеры"] += 1
        elif c == 9:
            type_dict[u"вода"] += 1
        elif str(c)[0] == '4': # 44,45 are for forest fires only
            type_dict[u"лес"] += 1
        elif c in range(100, 200) or c == 7:
            type_dict[u"изменения"] += 1
        # elif :
        #     type_dict["full"] += 1
        elif c == 24:
            type_dict[u"свалки"] += 1
        elif str(c)[0] == 8:
            type_dict[u"зарастание"] += 1
        elif str(c)[0] == '5' and c != 54:
            type_dict[u"дома"] += 1
        elif c == 25:
            type_dict[u"ТБО"] += 1
        elif c == 54:
            type_dict[u"дороги"] += 1
        elif c == 44 or c == 45:
            type_dict[u"гари"] += 1
    return type_dict


###################################################################################

t = datetime.now()
# Найти пары снимок-вектор для создания масок
if input_from_report:
    input = xls_to_dict(input_from_report)
    print('Input taken from %s' % input_from_report)
else:
    if vin is None or vin == '':
        input = get_pair_paths(pin, pms=pms)
    else:
        vecids = None
        if vecids_path is not None:
            if os.path.exists(vecids_path):
                with open(vecids_path) as vecids_data:
                    vecis = vecids_data.read().split('\n')
        raster_paths = get_raster_paths(pin)
        input = get_pairs(raster_paths, vin, image_col, vecids=vecids, split_vector=split_vector, pms=pms)
    # scroll(input, header='Source layers:')
    print('Input collected for {}'.format(datetime.now()-t))

scroll(input)
# sys.exit()

# Создать пути для размещения изображений и масок
suredir(pout)
'''
print('\nILLEGAL APPENDING EXTRA IMAGES:')
illegally_appended = 0
for file in folder_paths(r'e:\rks\razmetka\set021__20200625__doobuchenie_MWT_MGR_MQR_MCN_MBD\image\kanopus',1,'tif'):
    f,n,e = split3(file)
    if n in input:
        print('Already in: %s' % n)
    else:
        input[n] = {'r': file, 'v': r'\\172.21.195.2\FTP-Share\ftp\train_data\set021__20200625__doobuchenie_MWT_MGR_MQR_MCN_MBD\vector\object_all_07072020_fixed.shp'}
        print('Illegally appended: %s' % n)
        illegally_appended += 1
print('%i OBJECTS ILLEGALLY APPENDED\n' % illegally_appended)
'''

# Создавать маски из найденных пар
t = datetime.now()

if not (re.search('^IMCH\d+$', imgid) or re.search('^IM\d+$', imgid)):
    raise Exception('\n  WRONG imgid: {}, "IM\d+" or "IMCH\d+" is needed\n'.format(imgid))
for i, neuroid in enumerate(input):
    if neuroid is None:
        continue
    paths = get_paths(pout, neuroid, maskid, imgid)
    if paths:
        img_out, msk_out = paths
        img_in = input[neuroid]['r']
        vec_in = input[neuroid]['v']
        img_out = set_image(img_in, img_out, overwrite=overwrite, band_reposition=None)
        input[neuroid]['img_out'] = img_out
        msk_out = set_mask(img_in, vec_in, msk_out, overwrite=overwrite)
        input[neuroid]['msk_out'] = msk_out
        if not msk_out.startswith('ERROR'):
            if replace_vals:
                try:
                    replace_values(msk_out, replace_vals)
                    input[neuroid]['report'] = 'SUCCESS'
                except:
                    print('Error replacing values: %s' % neuroid)
                    input[neuroid]['report'] = 'ERROR: Mask names not replaced'
            else:
                input[neuroid]['report'] = 'SUCCESS'
            vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))

            all_codes = check_type(vals)
            max_type = max(all_codes, key=lambda key: all_codes[key])
            if max_type != maskid:
                print("Warning: masktype %s mismatch maskid %s" % (max_type, maskid))
            msk_values = ' '.join(flist(vals, str))
            try:
                vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))

                all_codes = check_type(vals)
                max_type = max(all_codes, key=lambda key: all_codes[key])
                if max_type != maskid:
                    print("Warning: masktype %s mismatch maskid %s" % (max_type, maskid))
                msk_values = ' '.join(flist(vals, str))
            except:
                print('Cannot get mask values for: %s' % neuroid)
                msk_values = ''
            input[neuroid]['msk_values'] = msk_values
            print('  %i -- MASKED: %s with %s\n' % (i + 1, neuroid, msk_values))
        else:
            print('  %i -- ERROR: %s\n' % (i + 1, neuroid))
    else:
        input[neuroid]['report'] = 'ERROR: Source paths not found'
        print('  %i -- ERROR: Source paths not found for %s\n' % (i + 1, neuroid))
try:
    if not (re.search('^IMCH\d+$', imgid) or re.search('^IM\d+$', imgid)):
        raise Exception('\n  WRONG imgid: {}, "IM\d+" or "IMCH\d+" is needed\n'.format(imgid))
    for i, neuroid in enumerate(input):
        if (neuroid is None) or input[neuroid]['pairing']==False:
            continue
        paths = get_paths(pout, neuroid, maskid, imgid)
        if paths:
            img_out, msk_out = paths
            img_in = input[neuroid]['r']
            vec_in = input[neuroid]['v']
            img_out = set_image(img_in, img_out, overwrite=overwrite, band_reposition=None)
            input[neuroid]['img_out'] = img_out
            msk_out = set_mask(img_in, vec_in, msk_out, overwrite=overwrite)
            input[neuroid]['msk_out'] = msk_out
            if not msk_out.startswith('ERROR'):
                if replace_vals:
                    try:
                        replace_values(msk_out, replace_vals)
                        input[neuroid]['report'] = 'SUCCESS'
                    except:
                        print('Error replacing values: %s' % neuroid)
                        input[neuroid]['report'] = 'ERROR: Mask names not replaced'
                else:
                    input[neuroid]['report'] = 'SUCCESS'
                '''
                vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))
                all_codes = check_type(vals)
                max_type = max(all_codes, key=lambda key: all_codes[key])
                if max_type != maskid:
                    print("Warning: masktype %s mismatch maskid %s" % (max_type, maskid))
                msk_values = ' '.join(flist(vals, str))
                '''
                try:
                    vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))
                    all_codes = check_type(vals)
                    max_type = max(all_codes, key=lambda key: all_codes[key])
                    if max_type != maskid:
                        print("Warning: masktype %s mismatch maskid %s" % (max_type, maskid))
                    msk_values = ' '.join(flist(vals, str))
                except:
                    print('Cannot get mask values for: %s' % neuroid)
                    msk_values = ''
                input[neuroid]['msk_values'] = msk_values
                print('  %i -- MASKED: %s with %s\n' % (i+1, neuroid, msk_values))
            else:
                print('  %i -- ERROR: %s\n' % (i + 1, neuroid))
        else:
            input[neuroid]['report'] = 'ERROR: Source paths not found'
            print('  %i -- ERROR: Source paths not found for %s\n' % (i + 1, neuroid))
except:
    print('\n ERROR CREATING MASK \n')
finally:
    report_name = 'report_{}.xls'.format(datetime.now()).replace(' ','_').replace(':','-')
    report_path = fullpath(pout, report_name)
    dict_to_xls(report_path, input)
    print('FINISHED -- REPORT SAVED TO %s' % report_path)
print(datetime.now()-t)

