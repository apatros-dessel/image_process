from geodata import *
from razmetka import Pansharp

path = r'\\172.21.195.2\thematic\!razmetka\errors_20210719_SR\Krim_KV\analog'

files = folder_paths(path,1,'tif')

data = {}
for file in files:
    name = Name(file)
    if '.PMS' in name:
        continue
    type = ('MS', 'PAN')['.PAN' in name]
    id = name.replace('.PAN','.MS')
    if id in data:
        data[id][type] = file
    else:
        data[id] = {type: file}
for id in data:
    pan_path = data[id].get('PAN')
    ms_path = data[id].get('MS')
    if not (None in (pan_path, ms_path)):
        pms_path = ms_path.replace('.MS','.PMS')
        if os.path.exists(pms_path):
            print('FILE EXISTS: %s' % pms_path)
        else:
            Pansharp(pan_path, ms_path, pms_path)
            # print('PANSHARPENED: %s' % Name(pms_path))
    else:
        print('ERROR: %s' % id)
