from image_processor import *
path2shp2 = r'c:\sadkov\toropez\image_test\full\Mosaic_20190405_1042_DEFLATE.shp'
path2shp1 = r'c:\sadkov\toropez\image_test\full\Mosaic_20190405_1044_DEFLATE.shp'
geodata.IntersectCovers(path2shp1, path2shp2, r'c:\sadkov\toropez\image_test\test.shp')