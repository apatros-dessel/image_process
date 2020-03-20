# -*- coding: utf-8 -*-

from geodata import *

path_in = r'd:\export\resursp\krym'
path_geom = r'd:\Krym\interface'
path_out = r'd:\Krym\interface'

attr_path_list = folder_paths(path_in, files=True, extension='json')
scroll(attr_path_list)
geom_path_input = folder_paths(path_geom, files=True, extension='shp')
scroll(geom_path_input)

geom_path_list = []
for attr_path in attr_path_list:
    unfound = True
    for geom_path in geom_path_input:
        basename = os.path.basename(attr_path)[:-5]
        print(basename)
        if basename in geom_path:
            geom_path_list.append(geom_path)
            unfound = False
            break
    if unfound:
        geom_path_list.append(None)

scroll(geom_path_list)

for attr_path, geom_path in zip(attr_path_list, geom_path_list):
    if (attr_path is None) or(geom_path is None):
        continue
    basename = os.path.basename(attr_path)
    out_path = fullpath(path_out, basename)
    change_single_geom(attr_path, geom_path, out_path)
