# -*- coding: utf-8 -*-
from geodata import *
path=r'C:\Users\admin\Desktop\07shp'
path_out = r'e:\test\07shp'
files = folder_paths(path, 1, 'SHP')
for file in files:
    file_out = (path_out + file[28:])
    # file_out = (path_out + file[28:]).decode('cp1251')
    ReprojectVector(file, file_out, 4326)
    print('File written: {}'.format(file_out))