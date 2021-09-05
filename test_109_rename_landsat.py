from tools import *

raster_files = folder_paths(r'd:\rks\razmetka_source', 1, 'tif')

vector_files = folder_paths(r'\\172.21.195.2\exchanger\!razmetka\Landsat_gari', 1, 'shp')
vector_names = flist(vector_files, lambda x: 'LC08_' + Name(x)[10:25])
#scroll(vector_names)

pout = r'd:\rks\razmetka_source\landsat_gari'
nofire_folder = r'd:\rks\razmetka_source\landsat_gari\nofire'
suredir(nofire_folder)

xls = xls_to_dict(r'\\172.21.195.2\exchanger\!razmetka\Landsat_gari\Снимки без гарей.xlsx')
nofires = []
for key in xls:
    id = xls[key].get('id', False)
    if id:
        nofires.append(id.replace(r'_refl.tif',''))

nofire_names = flist(nofires, lambda x: 'LC08_' + x[10:25])
# scroll(nofire_names)
# sys.exit()

for raster in raster_files:
    rname = Name(raster)
    if rname in vector_names:
        new_folder = pout + os.path.split(raster)[0].split(r'razmetka_source')[-1]
        suredir(new_folder)
        new_raster = fullpath(new_folder, Name(vector_files[vector_names.index(rname)]), 'tif')
        # print(rname, new_raster)
        copyfile(raster, new_raster)
        # rename(raster, raster.replace(rname, vector_files[vector_names.index(rname)]))
        continue
    elif rname in nofire_names:
        new_raster = fullpath(nofire_folder, nofires[nofire_names.index(rname)], 'tif')
        copyfile(raster, new_raster)
    else:
        print('NOT FOUND ' + rname )

