# -*- coding: utf-8 -*-

from geodata import *

pin = [r'\\172.21.195.2\FTP-Share\ftp\proc\resurs\krym_grn']                  # Путь к исходным файлам (растровым или растровым и векторным), можно указать список из нескольких директорий
vin = r'e:\rks\neuro\wastes_new\shp_for_masks\eco_KRYM_SIMFEROPOLSKIY_20191209.shp'     # Путь к векторному файлу масок (если None или '', то ведётся поиск векторных файлов в директории pin)
pout = r'e:\rks\razmetka\set031_svalki'                  # Путь для сохранения конечных файлов
maskid = 'MWS'                # Индекс масок (MWT, MFS и т.д.)
image_col = 'resurs_grn'              # Название колонки идентификатора растровой сцены (если vin != 0)
code_col = 'gridcode'               # Название колонки с кодовыми значениями
compress = 'DEFLATE'        # Алгоритм сжатия растровых данных
overwrite =  False          # Заменять существующие файлы
pms = True                  # Использовать паншарпы
replace_vals = None         # Изменить значения в конечной маске в соответствии со словарём, если None, то замены не производится
# report_xls = r''

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Resurs name
def parse_resurs(id):
    satid, loc1, sentnum, geoton, date, num1, ending = id.split('_')
    ending = ending.split('.')
    if len(ending)==4:
        num2, scn, type, lvl = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, ''
    elif len(ending)==5:
        num2, scn, type, lvl, grn = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn
    else:
        raise Exception('Wrong ending length for %s' % id)

# Parse Sentinel name
def parse_sentinel(id):
    # S2B_MSIL1C_20190828T043709_N0208_R033_T48VUP_20190828T082130
    satid, lvl, datetime, col, row, tile, datetime2 = id.split('_')
    lvl = lvl[-3:]
    date, time = datetime.split('T')
    return satid, date, time, tile, lvl

def get_neuroid(id):
    if re.search(r'KV.+L2', id):
        id = re.search(r'KV.+L2', id).group()
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[3:]
        if type=='PMS':
            lvl += type
    elif re.search(r'RP.+L2.GRN\d+', id):
        id = re.search(r'RP.+L2.GRN\d+', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = parse_resurs(id)
        loc = loc1 + scn[3:] + grn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^S2.+\d+T\d+$' ,id):
        satid, date, time, loc, lvl = parse_sentinel(id)
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = 'IM4-%s-%s-%s-%s' % (satid, date, loc, lvl)
    return neuroid

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

def filter_id(id, pms=False):
    for tmpt in (r'KV.+SCN\d+', r'IM4-KV.+-L2', r'IM4-KV.+\d{2,}', r'^S2.+\d+T\d+$', r'RP.+L2.GRN\d+'):
        search = re.search(tmpt, id)
        if search:
            report = search.group()
            if report.startswith('IM4'):
                if not report.endswith('-L2'):
                    report += '-L2'
                if pms:
                    report += 'PMS'
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
    export = []
    for folder in obj2list(raster_path):
        export.extend(folder_paths(folder, 1, 'tif'))
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

# Получить пути к исходным данным для масок для разделённых векторных файлов
def get_pair_paths(pin, pms = False):
    export = OrderedDict()
    for folder in obj2list(pin):
        paths = folder_paths(folder, 1)
        for path in paths:
            f,n,e = split3(path)
            id = get_neuroid(n)
            if id is None:
                continue
            if pms_exit(id, pms):
                continue
            if e=='tif':
                if id in export:
                    export[id]['r'] = path
                else:
                    export[id] = {'r': path}
            elif e in ('shp', 'json'):
                if id in export:
                    export[id]['v'] = path
                else:
                    export[id] = {'v': path}
    for id in export:
        if not (('v' in export[id]) and ('r' in export[id])):
            export.pop(id)
    return export

# Получить пути к исходным данным для масок для цельных векторных файлов
def get_pairs(raster_paths, vin, img_colname, pms=False):
    export = OrderedDict()
    def name_(path):
        return split3(path)[1]
    vecids = get_col_keys(vin, img_colname)
    for vecid in vecids:
        id = filter_id(vecid, pms=pms)
        for i, rasterid in enumerate(flist(raster_paths, name_)):
            if id==rasterid:
                export[get_neuroid(id)] = {'r': raster_paths[i], 'v': filter_dataset_by_col(vin, img_colname, vecid)}
                break
    for id in export:
        if not (('v' in export[id]) and ('r' in export[id])):
            export.pop(id)
    return export

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
    print(split3(f)[1], list(np.unique(gdal.Open(f).ReadAsArray())))

if vin is None or vin == '':
    input = get_pair_paths(pin, pms=True)
else:
    raster_paths = get_raster_paths(pin)
    input = get_pairs(raster_paths, vin, image_col, pms=pms)

scroll(input, header='Source layers:')

suredir(pout)

for i, neuroid in enumerate(input):
    img_out = fullpath(pout,neuroid,'tif')
    if not check_exist(img_out, overwrite):
        shutil.copyfile(input[neuroid]['r'], img_out)
    msk_out = fullpath(pout,maskid+neuroid[3:],'tif')
    if not check_exist(msk_out, overwrite):
        crs = get_srs(gdal.Open(img_out))
        vec_filtered = input[neuroid]['v']
        vec_reprojected = tempname('shp')
        vec_to_crs(ogr.Open(vec_filtered), crs, vec_reprojected)
        if not os.path.exists(vec_reprojected):
            vec_reprojected = vec_filtered
        print(vec_reprojected)
        RasterizeVector(vec_reprojected, img_out, msk_out, data_type = 2,
                        value_colname=code_col, compress=compress, overwrite=overwrite)
        if replace_vals:
            try:
                replace_values(msk_out, replace_vals)
            except:
                pass
    print('%i mask written: %s' % (i+1, neuroid))