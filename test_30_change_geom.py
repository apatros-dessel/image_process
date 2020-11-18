# -*- coding: utf-8 -*-

from geodata import *

path_in = r'd:\export\resursp\krym'
path_geom = r'd:\Krym\interface'
path_out = r'D:/resurs_p+/test'

attr_path_list = folder_paths(path_in, files=True, extension='json')
attr_path_list = [r'd:\export\resursp\krym\RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2\RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2.json']
'''
geom_path_input = folder_paths(path_geom, files=True, extension='shp')

geom_path_list = []
for attr_path in attr_path_list:
    unfound = True
    for geom_path in geom_path_input:
        basename = os.path.basename(attr_path)[:-5]
        if basename in geom_path:
            geom_path_list.append(geom_path)
            unfound = False
            break
    if unfound:
        geom_path_list.append(None)
'''
geom_path_list = [r'D:/resurs_p+/RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2_obrez_ref.json']

suredir(path_out)

for attr_path, geom_path in zip(attr_path_list, geom_path_list):
    if (attr_path is None) or(geom_path is None):
        continue
    basename = os.path.basename(attr_path)
    out_path = fullpath(path_out, basename)
    change_single_geom(attr_path, geom_path, out_path)
