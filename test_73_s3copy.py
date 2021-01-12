from geodata import *

path_in = r'\\172.21.195.215\thematic\products\s3\resursp'
area_vec = r'C:/Users/admin/Desktop/region69.shp'
path_out = r'\\172.21.195.215\thematic\ЦЗ_диск\Тверская область\Космические снимки\Ресурс П\PMS'
copy_ = True

area_ds, area_lyr = get_lyr_by_path(area_vec)
if area_lyr is None:
    sys.exit()
area_srs = area_lyr.GetSpatialRef()
copy_list = []
json_list = []
folders = folder_paths(path_in)[0][1:]
for folder in folders:
    json_path = fullpath(folder, os.path.split(folder)[1], 'json')
    if os.path.exists(json_path):
        meta_ds, meta_lyr = get_lyr_by_path(json_path)
        if meta_lyr:
            meta_feat = meta_lyr.GetNextFeature()
            if meta_feat is None:
                continue
            meta_geom = meta_feat.GetGeometryRef()
            meta_srs = meta_lyr.GetSpatialRef()
            if meta_srs!=area_srs:
                coordTrans = osr.CoordinateTransformation(meta_srs, area_srs)
                meta_geom.Transform(coordTrans)
            area_lyr.ResetReading()
            for area_feat in area_lyr:
                area_geom = area_feat.GetGeometryRef()
                if meta_geom.Intersects(area_geom):
                    id = os.path.split(folder)[1]
                    copy_list.append(id)
                    json_list.append(json_path)
                    if copy_:
                        copydir(folder, path_out)
                        print('COPY: %s' % id)
                    break
        else:
            print('Meta lyr is empty: %s' % json_path)
    else:
        print('Path not found: %s' % json_path)
if copy_list:
    with open(fullpath(path_out, 'scene_list.txt'), 'w') as txt:
        txt.write('\n'.join(copy_list))
if json_list:
    unite_vector(json_list, fullpath(path_out, 's3cover.shp'))
    print('TOTAL COVER OF %i SCENES' % len(json_list))
sys.exit()

# intersects = intersect_array(area_vec, s3cover)[0]

for intersect, folder in zip(intersects, folders):
    if intersect and (folder is not None):
        copydir(folder, path_out)
        print('COPY: %s' % os.path.split(folder)[1])