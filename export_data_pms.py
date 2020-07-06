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

def get_pms_json_from_ms(path_cover, path_out, pms_id, pms_raster_path=''):

    if os.path.exists(path_out):
        old_ds, old_lyr = get_lyr_by_path(path_out)
        if len(old_lyr) > 0:
            return 0

    print('Original PMS data not found for %s, collecting data from MS' % pms_id)

    if not os.path.exists(path_cover):
        print('Cannot find path: {}'.format(path_cover))
        return 1

    ms_id = pms_id.replace('.PMS', '.MS')
    filter_dataset_by_col(path_cover, 'id', ms_id, path_out=path_out)

    pms_ds, pms_lyr = get_lyr_by_path(path_out, 1)

    feat = pms_lyr.GetNextFeature()
    feat.SetField('id', pms_id)
    feat.SetField('id_neuro', feat.GetField('id_neuro') + 'PMS')
    feat.SetField('type', 'PMS')

    if os.path.exists(pms_raster_path):
        pms_data = gdal.Open(pms_raster_path)
    else:
        pms_data = None
    if pms_data is not None:
        feat.SetField('rows', int(pms_data.GetYSize))
        feat.SetField('cols', int(pms_data.GetXSize))
        feat.SetField('x_size', float(pms_data.GetGeoTransform[0]))
        feat.SetField('y_size', -float(pms_data.GetGeoTransform[5]))
    else:
        pan_id = pms_id.replace('.PMS', '.PAN')
        tpan_path = filter_dataset_by_col(path_cover, 'id', pan_id)
        pan_ds, pan_lyr = get_lyr_by_path(tpan_path)
        pan_feat = pan_lyr.GetNextFeature()
        feat.SetField('rows', int(pan_feat.GetField('rows')))
        feat.SetField('cols', int(pan_feat.GetField('cols')))
        feat.SetField('x_size', float(pan_feat.GetField('x_size')))
        feat.SetField('y_size', float(pan_feat.GetField('y_size')))
    # feat.SetField('area', None)

    pms_lyr.SetFeature(feat)

    pms_ds = None

    print('PMS data successfully written for for %s' % pms_id)

    return 0


dir_in = r'd:\terratech\kanopus_pms\krym_new'        # Путь к папке с исходными данными
dir_out = r'd:\terratech\s3\krym_new'    # Путь к месту хранения конечных данных
json_in = r'e:\rks\source\kanopus\2020-06-19\Krym_fullcover_new.json' # Путь к векторному файлу покрытия

ms_list = os.listdir(dir_in)
ms_list = flist(folder_paths(dir_out,1,'tif'), os.path.basename)
path_dict = {'ms': dir_in, 'json': json_in}
path_dict = {'json': json_in}

id_list = []
for name in ms_list:
    id, ext = os.path.splitext(name)
    ext = ext.replace('.','')
    if (ext in ['tif', 'tiff', 'tif']) and id.endswith('.PMS.L2'):
        id_list.append(id)

err_list = []

for id in id_list:
    id_dir = ('%s\\%s' % (dir_out, id))
    suredir(id_dir)
    for key in path_dict:
        if key == 'ms':
            name = (id + '.tif')
            try:
                shutil.move('%s\\%s' % (path_dict[key], name),
                                '%s\\%s' % (id_dir, name))
            except:
                err_list.append(name)
        elif key == 'json':
            name = id + '.json'
            path_out = '%s\\%s' % (id_dir, name)
            try:
                filter_dataset_by_col(path_dict['json'], 'id', id, path_out=path_out)
                # filter_geojson(path_dict['json'], 'id', id, '%s\\%s' % (id_dir, name))
                get_pms_json_from_ms(path_dict['json'], path_out, id)
                json_fix_datetime(path_out) # Fixes error with Python OGR datetime data
            except:
                err_list.append(name)

if len(err_list) > 0:
    for id in err_list:
        print(id)
    print('%i ERRORS FOUND' % len(err_list))
else:
    print('SUCCESS')
