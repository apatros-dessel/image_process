from image_processor import *
import shutil
import math

path_in = r'd:\kanopus_new\rgb\Tver_new'
path_out = r'd:\kanopus_new\rgb\Samara_error'

vector_cover_path = r'C:/Users/admin/Desktop/tver_contour.shp'

for file in os.listdir(path_in):

    file_path = fullpath(path_in, file)

    if geodata.gdal.Open(file_path) is not None:
        shp_path = tempname('shp')
        geodata.RasterDataMask(file_path, shp_path)
        if not geodata.ShapesIntersect(shp_path, vector_cover_path):
            shutil.copyfile(file_path, fullpath(path_out, file))
            print('File moved: %s' % file)
        else:
            print('File not moved: %s' % file)
    else:
        print('Error reading file: %s' % file)