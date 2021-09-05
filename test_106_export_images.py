from geodata import *

region_table = xls_to_dict(r'e:\rks\Fires_Yakutia\Якутия.xlsx', sheetnum=1)
export_folder = r'\\172.21.195.2\exchanger\!razmetka\FIRES_Yakutia\Landsat'
uluses = os.listdir(export_folder)
images = folder_paths(r'd:\rks\Fires_Yakutia\swir_8bit\Landsat',1,'tif')
names = flist(images, Name)

for num in region_table:
    line = region_table[num]
    ulus = line.get('Районы')
    if ulus:
        for folder in uluses:
            if folder in ulus:
                id = line.get('id снимка')
                if id:
                    path_out = r'%s\%s\%s.tif' % (export_folder, folder, id)
                    if not os.path.exists(path_out):
                        name = id[:5] + id[10:26] + 'SWIR_8bit'
                        if name in names:
                            file = images[names.index(name)]
                            copyfile(file, path_out)
                            print('WRITTEN: %s' % path_out)
