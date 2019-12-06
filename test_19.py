# Raster calculator

from image_processor import *

path2scene = r'D:\rks\forest\LC08_L1TP_136020_20160616_20170324_01_T1\LC08_L1TP_136020_20160616_20170324_01_T1_MTL.txt'
path2export = r'C:\sadkov\temp\nd_test.tif'

s = scene(path2scene)
red = s.getband('red')
print(red.file)
#nir = s.getband('nir')

#geodata.normalized_difference([red, nir], path2export)
