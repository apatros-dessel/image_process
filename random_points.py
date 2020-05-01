import math
import os
from geodata import RandomPointsInside, RandomLinesInside, RandomLinesRectangle

path_in = r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1\rectangle_kursk.shp'

path_patches = r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1\kursk_arkh_1.shp'

path_out = r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1\random_lines.shp'

os.chdir(r'd:\Sadkov\RNF\SUBSIDENCE\areas\kursk1')

# print('Here')

# RandomPointsInside(path_in, path_out)

# RandomLinesInside(path_in, path_out, random_azimuth=False)

RandomLinesRectangle(path_in, path_out, lines_num=1000, invert_axis=True, path_patches=path_patches,
                     filter_field='kod', filter_values=[0,1])