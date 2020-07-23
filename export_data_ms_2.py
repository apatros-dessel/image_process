# -*- coding: utf-8 -*-

from geodata import *
import shutil

dir_in = r'\\172.21.195.2\Development\TT-NAS-Archive\NAS-Archive-2TB-4\resursp_grn'        # Путь к папке с исходными данными
dir_out = r'e:\rks\resurs_granules_new'    # Путь к месту хранения конечных данных
json_in = r'E:/rks/resurs_otbor1.shp' # Путь к векторному файлу покрытия
id_xls = r'C:\Users\admin\Desktop\granules_selected.xls' # Путь к таблице xls с перечнем id отобранных снимков

# Find filenames in a folder by id
def find_path_by_id(id_dict, dir, ext='tif'):
    if isinstance(id_dict, list):
        id_dict = OrderedDict()
    paths = folder_paths(dir, 1, ext)
    for id in id_dict:
        miss = False
        for i, path in enumerate(paths):
            f, n, e = split3(path)
            if id==n:
                id_dict[id] = paths.pop(i)
                print(id_dict[id])
                found = True
                break
        if miss:
            id_dict[id] = None
    return id_dict

def filter_geojson(path_in, field, vals, path_out):

    ds = ogr.Open(path_in)
    lyr = ds.GetLayer()

    if not isinstance(vals, (list, tuple)):
        vals = [vals]

    new_ds = json(path_out, 1)

    new_lyr = new_ds.GetLayer()
    new_lyr.SetSpatialReference(lyr.GetSpatialReference())
    lyr_defn = lyr.GetLayerDefn()

    for key in lyr.GetNextFeature().keys():
        new_lyr.CreateField(lyr_defn.GetFieldDefn(lyr_defn.GetFieldIndex(key)))

    lyr.ResetReading()

    for feat in lyr:
        # print(feat.GetField(feat.GetFieldIndex(field)))
        feat_val = feat.GetField(feat.GetFieldIndex(field))
        if feat_val in vals:
            new_lyr.CreateFeature(feat)
            if unique_vals:
                vals.pop(vals.index(feat_val))

    new_ds = None

ms_dict = find_path_by_id(xls_to_dict(id_xls), dir_in)
path_dict = {'ms': dir_in, 'json': json_in}
#scroll(ms_dict)

err_list = []

for i, id in enumerate(ms_dict):
    id_dir = ('%s\\%s' % (dir_out, id))
    suredir(id_dir)
    name = (id + '.tif')
    # shutil.copyfile(ms_dict[id], '%s\\%s' % (id_dir, name))
    try:
        shutil.copyfile(ms_dict[id], '%s\\%s' % (id_dir, name))
    except:
        err_list.append(name)

    name = (id + '.json')
    path_out = '%s\\%s' % (id_dir, name)
    print(path_dict['json'])
    # filter_dataset_by_col(path_dict['json'], 'id', id, path_out=path_out)
    try:
        filter_dataset_by_col(path_dict['json'], 'id', id, path_out=path_out)
        json_fix_datetime(path_out) # Fixes error with Python OGR datetime data
    except:
        err_list.append(name)

    print('%i Scene written: %s' % (i+1, id))


if len(err_list) > 0:
    for id in err_list:
        print(id)
    print('%i ERRORS FOUND' % len(err_list))
else:
    print('SUCCESS')
