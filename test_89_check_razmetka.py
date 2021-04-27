from tools import *

razmetka_path = r'e:\rks\razmetka'
out_xls = r'e:\rks\razmetka\razmetka_report.xls'

def ReadXlsMeta(xls_path):
    data = xls_to_dict(xls_path)
    scn_num = len(data)
    raster_folders = {}
    values = []
    for id in data:
        if not data[id].get('msk_out'):
            continue
        raster = os.path.split(split3(data[id].get('r'))[0])[1]
        if raster is not None:
            if not raster in raster_folders:
                raster_folders[raster] = 1
            else:
                raster_folders[raster] += 1
        scn_values = data[id].get('msk_values')
        if scn_values is not None:
            scn_values = flist(str(scn_values).strip().split(' '), int)
            for val in scn_values:
                if not val in values:
                    values.append(val)
    values.sort()
    return scn_num, raster_folders, values

def DictToLine(dict_):
    str_ = ''
    for key in dict_:
        str_ += '%s: %s, ' % (str(key), str(dict_[key]))
    return str_[:-2]

folders = FolderDirs(razmetka_path)
final_report = OrderedDict()

for razmetka_id in folders:
    if '__QL' in razmetka_id:
        continue
    folder = folders[razmetka_id]
    razmetka_report = OrderedDict()
    xls_files = folder_paths(folder,1,'xls',filter_folder='quicklook')
    if len(xls_files)>0:
        xls_path = xls_files[0]
        scn_num, raster_folders, values = ReadXlsMeta(xls_path)
        scroll(raster_folders, header='\n%s: %s' % (razmetka_id, scn_num), lower=' '.join(flist(values, str)))
        razmetka_report['Всего сцен'] = scn_num
        razmetka_report['По типам'] = DictToLine(raster_folders)
        razmetka_report['Значения'] = ' '.join(flist(values, str))
    final_report[razmetka_id] = razmetka_report

dict_to_xls(out_xls, final_report)