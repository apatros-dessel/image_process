# -*- coding: utf-8 -*-

from geodata import *
import shutil

# Filter geojson vector layer by attribute
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

dir_in = r'd:\terratech\Krym_areas\rgbn_fin'        # Путь к папке с исходными данными
dir_out = r'd:\terratech\export\krym_resurs_pms'    # Путь к месту хранения конечных данных
json_in = r''                                       # Путь к векторному файлу покрытия

ms_list = os.listdir(dir_in)
path_dict = {'ms': dir_in, 'json': json_in}

id_list = []
for name in ms_list:
    id, ext = os.path.splitext(name)
    ext = ext.replace('.','')
    if (ext in ['tif', 'tiff', 'tif']) and id.endswith('.MS.L2'):
        id_list.append(id)

err_list = []

for id in id_list:
    id_dir = ('%s\\%s' % (dir_out, id))
    suredir(id_dir)
    for key in path_dict:
        if key == 'ms':
            name = (id + '.tif')
            try:
                shutil.copyfile('%s\\%s' % (path_dict[key], name),
                                '%s\\%s' % (id_dir, name))
            except:
                err_list.append(name)
        elif key == 'json':
            name = id + '.json'
            path_out = '%s\\%s' % (id_dir, name)
            try:
                filter_dataset_by_col(path_dict['json'], 'id', id, path_out=path_out)
                # filter_geojson(path_dict['json'], 'id', id, '%s\\%s' % (id_dir, name))
                json_fix_datetime(path_out) # Fixes error with Python OGR datetime data
            except:
                err_list.append(name)

if len(err_list) > 0:
    for id in err_list:
        print(id)
    print('%i ERRORS FOUND' % len(err_list))
else:
    print('SUCCESS')
