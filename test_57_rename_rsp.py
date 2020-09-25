from tools import *

raster_path = r'e:\rks\resurs_crimea\Zagorskoe'
xml_path = r'i:\Resurs_Krym'
output_path = r'e:\rks\resurs_crimea\Zagorskoe_fin'
suredir(output_path)

def parse_stinky_resursp(name):
    parts = name.split('_')
    if len(parts)==9:
        type = 'PAN'
        # channel = 'PAN'
    else:
        type = 'MS'
    id = '_'.join(parts[1:8])
    return id

def parse_raster_name(name):
    if 'REP' in name:
        return ''
    name1 = name.split('G')[0]
    name_parts = name1.split('_')[1:]
    name2 = '_'.join(name_parts)+'G'
    return name2

input = {}

raster_paths = folder_paths(raster_path,1,'tif')
raster_names = flist(raster_paths, lambda x: parse_raster_name(split3(x)[1]))
xml_paths = folder_paths(xml_path,1,'xml')
xml_names = flist(xml_paths, lambda x: parse_stinky_resursp(split3(x)[1]))

scroll(raster_names)
scroll(xml_names)

for i, id in enumerate(xml_names):
    if id in raster_names:
        input[id] = {'m': xml_paths[i], 'r': raster_paths[raster_names.index(id)]}

scroll(input)

for id in input:
    xml = input[id]['m']
    tif = input[id]['r']
    f, n, e = split3(xml)
    fr,n1,n2,loc1,n3,loc2,loc3,*parts = n.split('_')
    txt = open(xml).read()
    # <dSceneDate>24/06/2019</dSceneDate>
    if re.search(r'<dSceneDate>.+</dSceneDate>', txt):
        date = re.search(r'<dSceneDate>.+</dSceneDate>', txt).group()[12:-13].replace('/','')
        date = date[-4:]+date[2:4]+date[:2]
    rsp_name = 'RP1_%s_%s_GEOTON_%s_%s_%s.SCN1.PMS.L2A' % (loc1, loc3, date, n1, n2)
    for end in ('', '.REP', '.REP.RGB'):
        rsp_path = fullpath(output_path, rsp_name+end, 'tif')
        if os.path.exists(rsp_path):
            print('FILE EXISTS: %s' % rsp_path)
        else:
            rsp_in = tif.replace('.tif', end+'.tif')
            shutil.copyfile(rsp_in, rsp_path)
            print('FILE WRITTEN: %s' % rsp_path)

