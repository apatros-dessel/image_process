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


dir_in = r'g:\rks\DE\processed\kanopus\Tver'
# dir_out = input('Enter export dir')
dir_out = r'd:\terratech\export\tver'

if os.path.exists(dir_in + '\\pms'):
    pms_path = dir_in + '\\pms'
    pms_list = os.listdir(pms_path)
else:
    sys.exit(1)

id_list = []
for name in pms_list:
    id, ext = os.path.splitext(name)
    ext = ext.replace('.','')
    if ext in ['tif', 'tiff', 'tif']:
        id_list.append(id)

path_dict = {}
for anc in ['ms', 'rgb', 'ql', 'img']:
    if os.path.exists('%s\\%s' % (dir_in, anc)):
        path_dict[anc] = '%s\\%s' % (dir_in, anc)

for file in os.listdir(dir_in):
    if file.endswith('json'):
        path_dict['json'] = '%s\\%s' % (dir_in, file)

# print(id_list)

err_list = []

for id in id_list:
    # print(id)
    id_dir = ('%s\\%s' % (dir_out, id)).replace('.PMS', '.MS')
    suredir(id_dir)
    for key in path_dict:
        if key == 'ms':
            continue
            name = (id + '.tif').replace('.PMS', '.MS')
            try:
                shutil.copyfile('%s\\%s' % (path_dict[key], name),
                                '%s\\%s' % (id_dir, name))
            except:
                err_list.append(name)
        elif key == 'json':
            name = id.replace('.PMS', '.MS') + '.json'
            path_out = '%s\\%s' % (id_dir, name)
            filter_dataset_by_col(path_dict['json'], 'id', id.replace('.PMS', '.MS'), path_out=path_out)
            json_fix_datetime(path_out)
            try:
                # filter_geojson(path_dict['json'], 'id', id, '%s\\%s' % (id_dir, name))
                pass
            except:
                err_list.append(name)
                # filter_geojson(path_dict['json'], 'id', id, '%s\\%s' % (id_dir, name))

        else:
            continue
            name = '%s.%s.tif' % (id, key.upper())
            try:
                shutil.copyfile('%s\\%s' % (path_dict[key], name),
                                '%s\\%s' % (id_dir, name))
            except:
                err_list.append(name)

if len(err_list) > 0:
    for id in err_list:
        print(id)
    print('%i ERRORS FOUND' % len(err_list))
else:
    print('SUCCESS')
