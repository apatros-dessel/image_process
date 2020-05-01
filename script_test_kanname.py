from image_processor import *

path_in = r'e:\planet_rgb'
files = folder_paths(path_in, files=True, extension='tif')

krym = xls_to_dict(r'd:\digital_earth\kanopus_new\vector\samara.xls').keys()

for file in files:
    for id in krym:
        if id in file:
            krym.pop(krym.index(id))
            break
scroll(krym, header='Krym:')


