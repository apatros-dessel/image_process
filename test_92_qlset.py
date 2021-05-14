from geodata import *

folder_in = r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_clouds\MS\img\&without_cloud_originals'
ql_size = 30

files = folder_paths(folder_in,1,'tif')

ql_dir = r'%s/QL%s' % (folder_in, str(ql_size))
suredir(ql_dir)

for file in files:
    if not '#' in file:
        MakeQuicklook(file, fullpath(ql_dir, r'%s__QL%s' % (Name(file), str(ql_size)), 'tif'), pixelsize=ql_size)
        print('DONE: %s' % Name(file))
    else:
        print('MISS: %s' % Name(file))