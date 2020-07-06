# -*- coding: utf-8 -*-

from geodata import *

path_raster_dict = {
    'MWT': r'd:\terratech\neuro\Planet\Planet LES',
    # 'MFS': r'D:/terratech/neuro/MASK_part2/quarry_KAN_sub_all.shp',
}

path_vector_dict = {
    'MWT': r'D:\terratech\neuro\Planet\cover_kanopus.shp',
    # 'MFS': r'D:/terratech/neuro/MASK_part2/quarry_KAN_sub_all.shp',
}

planet_cover = r'D:/terratech/neuro/Planet/Tver_Planet_cover.json'
kanopus_cover = r'D:\terratech\neuro\Planet\Tver_Kanopus_cover_unite.json.geojson'
path_out = r'e:\test\razmetka\data\set023'

img_colname = 'id'      # Название векторного поля, содержащего id растра
obj_index_col = 'GRIDCODE'  # Название векторного поля, содержащего id объекта
compression = 'DEFLATE'     # Алгоритм сжатия растровых данных
overwrite =  False          # Заменять существующие файлы

report_xls = r'e:\test\razmetka\data\set023.xls'

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
    elif id.endswith(r'_3B_AnalyticMS'):
        parts = id[:-14].split('_')
        date = parts[0]
        satid = 'PLN%s' % parts[-1]
        if len(parts)==3:
            loc = parts[1]
        elif len(parts)==4:
            loc = parts[1] + parts[2]
        else:
            print('Unparsable id: %s' % id)
            raise Exception
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = 'IM4-%s-%s-%s-L2' % (satid, date, loc)
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

def filter_id(id):
    for tmpt in (r'KV.+SCN\d+', r'IM4-KV.+-L2', r'IM4-KV.+\d{2,}'):
        search = re.search(tmpt, id)
        if search:
            report = search.group()
            if report.startswith('IM4') and not report.endswith('-L2'):
                report += '-L2'
            elif report.startswith('KV'):
                report = report.replace('_SCN', '.SCN') + '.MS.L2'
                # report = get_neuroid(report)
            return report

def check_nonzeros(path):
    l = len(np.unique(gdal.Open(path),GetRasterBand(1).ReadAsArray()))
    print(l)
    return bool(l)

def name(path):
    return split3(path)[1]

baseline = OrderedDict()
for key in ('id', 'img', 'img_out', 'MWT', 'MFS'):
    baseline[key] = ''


# shp_list = folder_paths(shp_path, 1, 'tif')
# shp_ids = flist(shp_list, name)

report = OrderedDict()
empty_masks = []
error_list = []
data_miss = []
suredir(path_out)

for maskid in path_raster_dict:

    img_list = folder_paths(path_raster_dict[maskid],1,'tif')
    raster_ids = flist(img_list, name)
    vec = path_vector_dict[maskid]

    for i, id in enumerate(raster_ids):
        print(id)
        report[id] = deepcopy(baseline)
        neuroid = get_neuroid(id)
        report[id]['neuroid'] = neuroid
        img = img_list[i]
        mask0 = filter_dataset_by_col(planet_cover, img_colname, id)
        ds0, lyr0 = get_lyr_by_path(mask0)
        # print(len(lyr0), mask0)
        mask = tempname('shp')
        Intersection(kanopus_cover, mask0, mask)
        ds1, lyr1 = get_lyr_by_path(mask)
        # print(len(lyr1), mask)
        img_out = fullpath(path_out, neuroid, 'tif')
        img_tmp = tempname('tif')
        try:
            clip_raster(img, mask, export_path=img_tmp, byfeatures=True, exclude=False, nodata=0,
                    path2newshp=None, compress='DEFLATE', overwrite=True)
        except:
            report[id]['result'] = 'Unclipped'
            continue
        SaveRasterBands(img_tmp, (3,2,1,4), img_out, options={'compress': 'DEFLATE'}, overwrite=True)
        os.remove(img_tmp)
        msk_out = r'%s\%s-%s.tif' % (path_out, maskid, neuroid[4:])
        print(msk_out)
        try:
            res = RasterizeVector2(vec, img, msk_out, value_colname=obj_index_col, compress=compression, overwrite=True)
        except:
            res = 1
        report[id]['result'] = res
        report[id][maskid] = vec
        report[id]['img_out'] = split3(img_out)
        report[id][maskid] = split3(msk_out)

dict_to_xls(report_xls, report)

if empty_masks:
    scroll(empty_masks, header='Empty masks:')

if error_list:
    scroll(error_list, header='Errors:')

if data_miss:
    scroll(data_miss, header='No data found:')

