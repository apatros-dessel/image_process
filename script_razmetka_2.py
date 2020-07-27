# -*- coding: utf-8 -*-

from geodata import *

# Перечень векторных файлов для создания масок, с указанием условного обозначения типа маски
path_shp_dict = {
    'MWS': r'\\172.21.195.2/FTP-Share/ftp/ТБО_нейросеть/Neiro_TBO_svalki_narushZem.shp'
}

# Перечни кодов в рамках каждой маски (чтобы разделять векторные файлы с несколькими типами масок)
gridcode = {
    'MQR':(1,10,11,12,13),
    'MWS':(2,24,25,26),
    'MGR':(2,20,21,22,23),
    'MGR':(2,20,21,22,23),
    'MCN':(3,30,31,32,33),
    'MBD':(5,51,52,53),
    'MWT':9,
}

# Перечни путей к корневым папкам растровых файлов
raster_path = [r'\\172.21.195.2\FTP-Share\ftp\db_etalons',
            # r'\\172.21.195.2\Development\TT-NAS-Archive\NAS-Archive-2TB-7\kan-pms',
               r'\\172.21.195.2\FTP-Share\ftp\proc\kanopus',
               r'\\172.21.195.2\FTP-Share\ftp\s3',
               # r'\\172.21.195.2\Development\TT-NAS-Archive\NAS-Archive-2TB-6\s3',
               # r'\\172.21.195.2\Development\TT-NAS-Archive\NAS-Archive-2TB-1\Kanopus',
               # r'\\172.21.195.2\Development\TT-NAS-Archive\NAS-Archive-2TB-2\Kanopus',
               # r'\\172.21.195.2\Development\TT-NAS-Archive\NAS-Archive-2TB-5\na-va',
               r'G:', r'K:',
               ]

# Путь для сохранения конечных файлов
path_out = r'e:\rks\razmetka\set028'

img_colname = 'name'      # Название векторного поля, содержащего id растра
obj_index_col = 'gridcode'  # Название векторного поля, содержащего id объекта
compression = 'DEFLATE'     # Алгоритм сжатия растровых данных
overwrite =  False          # Заменять существующие файлы
pms = False                  # Использовать паншарпы

report_xls = r'e:\rks\razmetka\set028_1.xls'

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

def get_neuroid(id):
    if id.startswith('KV'):
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[3:]
        if type=='PMS':
            lvl += type
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
    for tmpt in (r'KV.+SCN\d+', r'IM4-KV.+-L2', r'IM4-KV.+\d{2,}'):
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

baseline = OrderedDict()
for key in ('id', 'img', 'img_out', 'MWT', 'MBD', 'MGR', 'MQR', 'MCN'):
    baseline[key] = ''

img_list = get_raster_paths(raster_path)

report = OrderedDict()
empty_masks = []
error_list = []
data_miss = []
suredir(path_out)

for maskid in path_shp_dict:

    # vec_path = path_shp_dict[maskid]
    vec_path = filter_dataset_by_col(path_shp_dict[maskid], obj_index_col, gridcode[maskid])
    print(vec_path)
    raster_ids = get_col_keys(vec_path, img_colname)
    scroll(raster_ids)

    for neuroid in raster_ids:
        trueid = filter_id(neuroid, pms = pms)
        if not trueid in report:
            report[trueid] = deepcopy(baseline)
            report[trueid]['id'] = neuroid
        if not trueid.startswith('IM4-'):
            checkval = get_neuroid(trueid)
        else:
            checkval = trueid
        for img in img_list:
            error = True
            f, n, e = split3(img)
            # print(checkval, trueid, n)
            if re.search(r'^\d+_2020_\d+\.', n):
                n = n[len(re.search(r'^\d+_2020_\d+\.', n).group())]
            if checkval==n or trueid==n:
            # if n.endswith(checkval) or n.endswith(trueid):
                error = False
                # print(checkval, n)
                report[trueid]['img'] = img
                if n.startswith('KV'):
                    img_name = get_neuroid(n)
                else:
                    img_name = n
                img_out = fullpath(path_out, checkval, e)
                msk_name = maskid + img_name[3:]
                msk_out = fullpath(path_out, msk_name, e)
                report[trueid][maskid] = vec_path
                report[trueid]['img_out'] = img_name
                report[trueid][maskid] = msk_name
                try:
                    if check_exist(msk_out, overwrite):
                        # print('Image already exists: %s' % img_name)
                        pass
                    else:
                        shutil.copyfile(img, img_out)
                    # SaveRasterBands(img, bands, r'%s\IMCH8_%s.tif' % (path_out, neuroid),
                                    # options={'compress': 'DEFLATE'}, overwrite=overwrite)

                    if check_exist(msk_out, overwrite):
                        # print('Mask already exists: %s' % msk_name)
                        pass
                    else:
                        crs = get_srs(gdal.Open(img_out))
                        vec_filtered = filter_dataset_by_col(vec_path, img_colname, neuroid)
                        # print(vec_filtered)
                        vec_reprojected = tempname('shp')
                        vec_to_crs(ogr.Open(vec_filtered), crs, vec_reprojected)
                        if not os.path.exists(vec_reprojected):
                            vec_reprojected = vec_filtered
                        # print(vec_reprojected)
                        RasterizeVector(vec_reprojected, img, msk_out,
                                        value_colname=obj_index_col, compress=compression, overwrite=overwrite)

                    if not check_nonzeros(msk_out):
                        print('Error -- empty mask: %s' % msk_name)
                        empty_masks.append(msk_name)
                        os.remove(msk_out)
                    else:
                        print('Mask written: %s' % neuroid)
                except:
                    error_list.append(msk_name)
                    print('Error writing: %s' % neuroid)
                break
        if error:
            data_miss.append(trueid)
            print('Raster data not found: %s' % trueid)

dict_to_xls(report_xls, report)

if empty_masks:
    scroll(empty_masks, header='Empty masks:')

if error_list:
    scroll(error_list, header='Errors:')

if data_miss:
    scroll(data_miss, header='No data found:')

