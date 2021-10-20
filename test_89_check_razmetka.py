from tools import *

razmetka_path = r'e:\rks\razmetka'
copy_mask_folder = r'e:\rks\copymask'
out_xls = r'e:\rks\razmetka\razmetka_report.xls'

def ReadXlsMeta(xls_path, copy_mask_folder=None):
    data = xls_to_dict(xls_path)
    folder = os.path.split(xls_path)[0]
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
                    if val is not None:
                        values.append(val)
        if copy_mask_folder is not None:
            msk_path = data[id].get('msk_out')
            if msk_path:
                msk_name = os.path.basename(msk_path)
                # msk_type = GetMaskBandType(msk_name)
                # msk_folder = r'%s/%s/%s' % (copy_mask_folder, msk_type, raster)
                msk_folder = r'%s/%s' % (copy_mask_folder, raster)
                suredir(msk_folder)
                if 'masks' in msk_path:
                    msk_folder_down = msk_path.split('masks')[1]
                    msk_source = r'%s/masks/%s' % (folder, msk_folder_down)
                    copyfile(msk_source, fullpath(msk_folder, msk_name))
                else:
                    print('Wrong msk_out: %s' % str(msk_path))
    values.sort()
    return scn_num, raster_folders, values

def GetMaskBandType(msk_name):
    if msk_name.startswith('IMR') or ('_red' in msk_name):
        return 'red'
    if msk_name.startswith('IMG') or ('_green' in msk_name):
        return 'green'
    if msk_name.startswith('IMB') or ('_blue' in msk_name):
        return 'blue'
    if msk_name.startswith('IMN') or ('_nir' in msk_name):
        return 'nir'
    if msk_name.startswith('IMP') or ('.PAN' in msk_name):
        return 'pan'
    if '.PMS' in msk_name:
        return 'pms'
    else:
        return 'ms'

def DictToLine(dict_):
    str_ = ''
    for key in dict_:
        str_ += '%s: %s, ' % (str(key), str(dict_[key]))
    return str_[:-2]

folders = FolderDirs(razmetka_path)
final_report = OrderedDict()

for razmetka_id in folders:
    # if ('__QL' in razmetka_id) and not ('resurs' in razmetka_id):
        # continue
    folder = folders[razmetka_id]
    razmetka_report = OrderedDict()
    xls_files = folder_paths(folder,1,'xls',filter_folder='quicklook')
    if len(xls_files)>0:
        xls_path = xls_files[0]
        scn_num, raster_folders, values = ReadXlsMeta(xls_path, copy_mask_folder=None)#fullpath(copy_mask_folder, razmetka_id))
        # scroll(raster_folders, header='\n%s: %s' % (razmetka_id, scn_num), lower=' '.join(flist(values, str)))
        razmetka_report['Всего сцен'] = scn_num
        razmetka_report['По типам'] = DictToLine(raster_folders)
        razmetka_report['Значения'] = ' '.join(flist(values, str))
    final_report[razmetka_id] = razmetka_report

dict_to_xls(out_xls, final_report)