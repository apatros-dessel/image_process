# Clips raster with shapefile

from geodata import *

path2raster_folder = r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\MS\img\img_surface_cloud_originals'
path2vector_folder = r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\MS\img\img_surface_cloud_cut\cut_mask'
path2export_folder = r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\MS\img\img_surface_cloud_cut'

vector_files = folder_paths(path2vector_folder,1,'shp')

# scroll(vector_files, counts=1)

for path2vector in vector_files:
    name = Name(path2vector)
    path2export = fullpath(path2export_folder, name, 'tif')
    if os.path.exists(path2export):
        print('FILE EXISTS: %s' % name)
    else:
        id = name.split('_cut')[0]
        path2raster = fullpath(path2raster_folder, id, 'tif')
        if os.path.exists(path2raster):
            clip_raster(path2raster, path2vector, path2export)
            print('WRITTEN: %s' % name)
        else:
            print('FILE NOT FOUND: %s' % path2raster)
