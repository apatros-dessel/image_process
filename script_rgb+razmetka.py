# -*- coding: utf-8 -*-

from image_processor import *
from PIL import Image

sat_rgb = {
    'PL': [3,2,1],
    'KV': [1,2,3],
    'RP': [1,2,3],
}

path = [
    # r'd:\digital_earth\resurs-p_new\krym\2074509_220120_Krym',
    r'd:\digital_earth\resurs-p_new\krym',
    ]

obj_of_interest =  [
    r'D:\digital_earth\data_2_razmetka\other\20200228\TBO_krym_point.shp',
]

folder = r'e:\kanopus_new'


if not os.path.exists(folder):
    os.makedirs(folder)

proc = process(output_path=r'e:\test')
proc.input(path)

print('Basic process of length %i' % len(proc))

''' FILTER WINTER SCENES '''

ids_list = proc.get_ids()
for id in ids_list:
    if not '.PMS.' in id:
        proc.del_scene(id)
        continue
    ascene = proc.get_scene(id)
    month = int(ascene.meta.datetime.month)
    if (month>10) or (month<4):
        proc.del_scene(id)

print('Filtered process of length %i' % len(proc))
proc.get_vector_cover(r'resursp_filtered_cover.json')

''' FIND SCENES FOR OBJECTS '''

input_list = []
qual_dict = {}

for shp_list in obj_of_interest:

    print(shp_list)
    #raise Exception

    obj_ds, obj_lyr = geodata.get_lyr_by_path(shp_list)

    for obj_feat in obj_lyr:

        obj_geom = obj_feat.GetGeometryRef()
        print(obj_geom.ExportToWkt())
        #raise Exception

        feat_id_list = []
        feat_dates_list = []

        for ascene in proc.scenes:

            scene_ds, scene_lyr = geodata.get_lyr_by_path(ascene.datamask())

            if scene_lyr is not None:

                if obj_lyr.GetSpatialRef() != scene_lyr.GetSpatialRef():
                    scene_ds = geodata.vec_to_crs(scene_ds, obj_lyr.GetSpatialRef(), tempname('shp'))
                    scene_lyr = scene_ds.GetLayer()

                for scene_feat in scene_lyr:
                    scene_geom = scene_feat.GetGeometryRef()
                    if obj_geom.Intersects(scene_geom):
                        feat_id_list.append(ascene.meta.id)
                        feat_dates_list.append(ascene.meta.datetime)
                        break

        feat_id_arr = np.array(feat_id_list)
        feat_dates_arr = np.array(feat_dates_list)
        sort = np.argsort(feat_dates_arr)[::-1]
        feat_id_arr = feat_id_arr[sort]
        feat_dates_arr = feat_dates_arr[sort]

        scroll(feat_id_arr)

        raise Exception

        for id in feat_id_arr:
            if id in input_list:
                break
            elif id in qual_dict:
                if qual_dict.get(id):
                    break
                else:
                    try:
                        with Image.open(ascene.quickllok()) as quicklook:
                            quicklook.show()
                            qualtest = input('Print zero if scene is of bad quality: ')
                            if qualtest != 0:
                                qual_dict[id] = True
                                input_list.append(id)
                                break
                            else:
                                qual_dict[id] = False
                    except:
                        print('Error making quicklook for {}'.format(id))

scroll(input_list)

raise Exception






''' GROUP SCENES BY SATELLITE AND DATE '''

raster_path_dict = {}
print('Start making rgb from %i scenes' % len(proc))

report = OrderedDict()


for ascene in proc.scenes:

    if ascene.imsys in ['LST', 'SNT']:
        # The script doesnt work for these image systems yet
        continue

    if ascene.imsys in ['KAN', 'RSP']:
        if not '.PMS.' in ascene.meta.id:
            continue

    if check_obj:
        if not geodata.ShapesIntersect(obj_of_interest, ascene.datamask()):
            continue

    strip_id = ascene.meta.name('[sat]-[date]')
    raster_path = ascene.get_band_path('red')[0]

    sat, date = strip_id.split('-')
    report[ascene.meta.id] = {'stripid': strip_id, 'sat': sat, 'date': date}

    if strip_id in raster_path_dict:
        raster_path_dict[strip_id].append(raster_path)
    else:
        raster_path_dict[strip_id] = [raster_path]

# scroll(raster_path_dict, header='Raster paths:')

sum = 0
for key in raster_path_dict:
    sum += len(raster_path_dict[key])
    scroll(raster_path_dict[key], header='Raster path for: %s' % key)
print(len(raster_path_dict), sum)

dict_to_xls(r'e:\test\resurs-p_ofinterest.xls', report)

raise Exception

errors_list = []

# border_list = geodata.GetRasterPercentiles(raster_path_dict[raster_path_dict.keys()[0]], min_percent = 0.01, max_percent = 0.995, band_num_list = [3,2,1], nodata = 0)

# print(border_list)

''' MAKING RGB FOR EACH GROUP '''
for strip_id in raster_path_dict:

    raster_path_list = raster_path_dict[strip_id]
    # band_hist_dict = [{},{},{}]
    # borders_list = []

    sat = strip_id[:2]

    path2export_list = []

    for path2raster in raster_path_list:
        path2export = r'{}\{}\{}\{}'.format(folder, sat, strip_id[-8:], os.path.split(path2raster)[1])
        if os.path.exists(path2export):
            print('File already exists: {}'.format(path2export))
        else:
            path2export_list.append((path2raster, path2export))

    if len(path2export_list) == 0:
        continue

    ''' MAKE HYSTOGRAMS FOR EACH GROUP '''
    borders_list = geodata.GetRasterPercentiles(raster_path_list, min_percent = 0.01, max_percent = 0.995, band_num_list = [3,2,1], nodata = 0)

    print('Start processing %i scenes' % len(path2export_list))

    ''' SAVING EVERY SCENE WITH THIS HYSTOGRAM '''
    for path2raster, path2export in path2export_list:
        if not os.path.exists(os.path.split(path2export)[0]):
            os.makedirs(os.path.split(path2export)[0])
        # path2export = r'{}\{}'.format(folder, os.path.split(path2raster)[1])
        # res = geodata.RasterToImage3(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], reprojectEPSG=3857, compress='LZW', overwrite=False, alpha=False)

        try:
            # res = geodata.RasterToImage2(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], compress='LZW', overwrite=False, alpha=False)
            res = geodata.RasterToImage3(path2raster,
                                         path2export,
                                         method=3,
                                         band_limits=borders_list,
                                         gamma=0.85,
                                         exclude_nodata=True,
                                         enforce_nodata=0,
                                         band_order=globals()['sat_rgb'].get(sat),
                                         reprojectEPSG = 3857,
                                         compress='LZW',
                                         overwrite=False,
                                         alpha=False)
        except:
            res = 1
        if res == 0:
            print('File written: {}'.format(path2export))
        else:
            print('Failed to write file: {}'.format(path2export))
            errors_list.append(path2export)

if len(errors_list) > 0:
    scroll(errors_list, header='Errors while procesing files:')

