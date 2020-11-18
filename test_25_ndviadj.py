from image_processor import *

path = r'd:\digital_earth\sentinel_crops\2019'

proc = process()
proc.input(path)

for ascene in proc.scenes:
    print(ascene.meta.name(r'e:\test\newsnt\NDVIadj-[date]-[location]-[lvl].tif'))
    ascene.calculate_index('NDVI', ascene.meta.name(r'e:\test\newsnt\NDVI-[date]-[location]-[lvl].tif'), compress='DEFLATE')
    # ascene.calculate_index('NDVIadj', ascene.meta.name(r'e:\test\newsnt\NDVIadj-[date]-[location]-[lvl].tif'), compress = 'DEFLATE')
    # ascene.calculate_index('NDVIadj', ascene.meta.name(r'e:\test\newsnt'), compress='DEFLATE')