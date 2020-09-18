# -*- coding: utf-8 -*-

from geodata import *

pin = r'd:\digital_earth\DG_сover_fin.json'

din, lin = get_lyr_by_path(pin,1)

id_dict = OrderedDict()
duplicates = OrderedDict()
remove_list = []
report_xls = r'd:\digital_earth\DG_cover_remove.xls'
report_json = r'd:\digital_earth\DG_cover_remove.json'
remove_area = 0.0
confirm_manually = False

for feat in lin:
    id = feat.GetField('id')
    path = feat.GetField('path')
    geom = feat.GetGeometryRef().ExportToWkt()
    check = '%ix%i' % (feat.GetField('rows'), feat.GetField('cols'))
    date = feat.GetField('datetime')
    satid = feat.GetField('sat_id')
    type = feat.GetField('type')
    if id in id_dict:
        if geom==id_dict[id][1]:
            if confirm_manually:
                print(id_dict[id][2], id_dict[id][3])
                print(check, date)
                remove = input('')
            else:
                remove = True
            if remove:
                if not id in duplicates:
                    duplicates[id_dict[id][0]] = OrderedDict()
                    duplicates[id_dict[id][0]]['id'] = id
                    duplicates[id_dict[id][0]]['satid'] = id_dict[id][4]
                    duplicates[id_dict[id][0]]['type'] = id_dict[id][5]
                    duplicates[id_dict[id][0]]['size'] = id_dict[id][2]
                    duplicates[id_dict[id][0]]['datetime'] = id_dict[id][3]
                    duplicates[id_dict[id][0]]['remove'] = False
                duplicates[path] = OrderedDict()
                duplicates[path]['id'] = id
                duplicates[path]['satid'] = satid
                duplicates[path]['type'] = type
                duplicates[path]['size'] = check
                duplicates[path]['datetime'] = date
                duplicates[path]['remove'] = True
                remove_list.append(feat.GetFID())
                continue
    id_dict[id] = (path, geom, check, date, satid, type)

scroll(duplicates)

scroll(remove_list, header='Remove FIDS:')
print(len(remove_list))
dict_to_xls(report_xls, duplicates)
filter_dataset_by_col(pin, 'path', duplicates.keys(), path_out=report_json)
din, lin = get_lyr_by_path(report_json,1)

print('Remove duplicates? Y/N')
answer = input('')

if answer:
    for fid in remove_list:
        lin.DeleteFeature(fid)

din = None
