from geodata import *
from razmetka import Pansharp

files = folder_paths(r'\\172.21.195.2\thematic\!razmetka\vivid\fin\Vivid',1,'tif')
keys = xls_to_dict(r'\\172.21.195.2\thematic\!razmetka\vivid\fin\Vivid_Kanopus_final.xlsx')
for viv in keys:
    #VectorizeRaster(file, fullpath(r'e:\temp',Name(file),'shp'), index_id='id', bandnum=1, overwrite=True)
    vivid = r'e:\temp\%s.shp' % viv
    kanms = r'\\172.21.195.2\thematic\!razmetka\vivid\fin\Kanopus\MS\%s.tif' % keys[viv]
    clip_raster(kan_ms, vivid, r'e:\temp\%s.tif' % keys[viv])
    # VectorizeBand((file, 1), fullpath(r'e:\temp',Name(file),'shp'), classify_table=[(0, None, 1)], index_id='CLASS', erode_val=0, overwrite=True)
sys.exit()

data = {}
for file in folder_paths(r'e:\rks\new',1,'tif'):
    name = Name(file)
    if '.PMS' in name:
        continue
    type = ('MS', 'PAN')['.PAN' in name]
    if re.search('_\d+$', name):
        number = int(name.split('_')[-1])
        if type == 'PAN':
            number -= 1
        id = name.split(type)[0] + 'MS_' + str(number)
    else:
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
