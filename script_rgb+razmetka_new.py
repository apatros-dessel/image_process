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
    r'F:\102_2020_116',
    ]

obj_of_interest =  [
    # r'D:\digital_earth\data_2_razmetka\other\20200228\TBO_krym_point.shp',
    r'f:\vector\Krym_quarry_comment.shp',
    r'f:\vector\TBO_krym_point.shp',
]

path2xls = r'f:\vector\kanopus_report.xls'

folder = r'f:\kanopus_new'


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

def intersect_array(shp1, shp2):
    ds1, lyr1 = geodata.get_lyr_by_path(shp1)
    if lyr1 is None:
        return None
    ds2, lyr2 = geodata.get_lyr_by_path(shp2)
    if lyr2 is None:
        return None
    int_arr = np.zeros((lyr1.GetFeatureCount(), lyr2.GetFeatureCount())).astype(bool)
    if lyr1.GetSpatialRef() != lyr2.GetSpatialRef():
        ds2 = geodata.vec_to_crs(ds2, lyr1.GetSpatialRef(), tempname('shp'))
        lyr2 = ds2.GetLayer()
    for i, feat1 in enumerate(lyr1):
        geom1 = feat1.GetGeometryRef()
        lyr2.ResetReading()
        for j, feat2 in enumerate(lyr2):
            geom2 = feat2.GetGeometryRef()
            int_arr[i,j] = geom1.Intersects(geom2)
    return int_arr

def layers_intersection_array(shapes_list, proc):
    scenes_list = []
    export_array = None
    for shp1 in shapes_list:
        result_array = None
        for ascene in proc.scenes:
            if result_array is None:
                result_array = intersect_array(shp1, ascene.datamask())
            else:
                new_array = intersect_array(shp1, ascene.datamask())
                if new_array is not None:
                    result_array = np.hstack([result_array, new_array])
        if export_array is None:
            export_array = result_array
        else:
            if result_array is not None:
                export_array = np.vstack([export_array, result_array])
    return export_array

def infullcloud(id):
    return int(id in globals()['full_cloud'])

''' FIND SCENES FOR OBJECTS '''

input_list = []
qual_dict = {}
full_cloud = []
error_list = []


intersection_array = layers_intersection_array(obj_of_interest, proc)

scene_ids = np.array(proc.get_ids())

scene_dates = []
for ascene in proc.scenes:
    scene_dates.append(ascene.meta.datetime)
scene_dates = np.array(scene_dates)

for i in range(intersection_array.shape[0]):

    feat_id_arr = scene_ids[intersection_array[i,:]]
    feat_dates_arr = scene_dates[intersection_array[i,:]]

    sort = np.argsort(feat_dates_arr)[::-1]
    feat_id_arr = feat_id_arr[sort]
    feat_dates_arr = feat_dates_arr[sort]

    scroll(feat_id_arr, header='Id list for feature %i:' % i)

    clouded_list = []
    approved = False

    for id in feat_id_arr:
        if id in input_list:
            approved = True
            print('Scene already in input_list: {}'.format(id))
            break
        elif id in qual_dict:
            if qual_dict.get(id):
                approved = True
                print('Scene previously approved: {}'.format(id))
                break
        else:
            try:
                with Image.open(proc.get_scene(id).quicklook()) as quicklook:
                    quicklook.show()
                    qualtest = input('Print 0 if scene is of bad quality or 10 if scene is covered with clouds: ')
                    if qualtest not in [0, 10]:
                        qual_dict[id] = True
                        input_list.append(id)
                        approved = True
                        print('Scene appended to input_list: {}'.format(id))
                        break
                    elif qualtest == 10:
                        clouded_list.append(id)
                    elif qualtest == 0:
                        qual_dict[id] = False
            except:
                print('Error making quicklook for {}'.format(id))

    if not approved:
        if len(clouded_list) == 0:
            error_list.append(i)
            print('Unable to find proper scenes for feature {}'.format(i))
        else:
            scroll(clouded_list, header='Cannot find proper scene, include clouded scenes too:')
            input_list.extend(clouded_list)
            full_cloud.extend(clouded_list)

scroll(input_list, header='Final input list:')

scroll(full_cloud, header='Full cloud list:')

scroll(error_list, header='Errors:')

report_dict = OrderedDict()
for id in input_list:
    ascene = proc.get_scene(id)
    report_dict[id] = {
        'fullpath': ascene.fullpath,
        'date': ascene.meta.name('[date]'),
        'filepath': ascene.get_band_path('red')[0],
        'datamask': ascene.datamask(),
        'quicklook': ascene.quicklook(),
        'clouds': infullcloud(id),
    }

dict_to_xls(path2xls, report_dict)

proc_new = process()
for id in input_list:
    proc_new.scenes.append(proc.get_scene(id))

print('%i scenes ready for making rgb' % len(proc_new))
