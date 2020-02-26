import math
import os
from geodata import RandomPointsInside, RandomLinesInside, RandomLinesRectangle

path_in_list = [
    r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1\rectangle_kursk.shp',
    r'D:\Sadkov\RNF\SUBSIDENCE\areas\kopetdag_vik5\kopetdag_vik5_rectangle.shp',
    r'D:/Sadkov/RNF/SUBSIDENCE/areas/janibek_station/janibek_station_rectangle.shp',
]

path_patches_list = [
    r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1\kursk_arkh_1.shp',
    r'D:/Sadkov/RNF/SUBSIDENCE/areas/kopetdag_vik5/kopetdag_vik5_areas.shp',
    r'D:/Sadkov/RNF/SUBSIDENCE/areas/JANIBEK_STATION_EDIT/janibek_station_edit1.shp',
]

path_out_list = [
    r'D:\Sadkov\RNF\SUBSIDENCE\areas\kursk1\random_test\random_lines.shp',
    r'D:/Sadkov/RNF/SUBSIDENCE/areas/kopetdag_vik5/random_test\random_lines.shp',
    r'D:/Sadkov/RNF/SUBSIDENCE/areas/JANIBEK_STATION_EDIT/random_test\random_lines.shp'
]

# os.chdir(r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1')

# print('Here')

# RandomPointsInside(path_in, path_out)

# RandomLinesInside(path_in, path_out, random_azimuth=False)

for path_in, path_patches, path_out in zip(path_in_list, path_patches_list, path_out_list):

    if not os.path.exists(os.path.dirname(path_out)):
        os.makedirs(os.path.dirname(path_out))

    RandomLinesRectangle(path_in, path_out, lines_num=1000, random_length=True, invert_axis=True, path_patches=path_patches, filter_field='kod', filter_values=[0,1])