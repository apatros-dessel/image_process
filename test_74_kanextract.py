from geodata import *
from image_processor import process, scene

xls_path = r'\\172.21.195.2\thematic\Sadkov_SA\kanopus_dymka\102_2020_1159\report (new_code).xls'
raster_data_path = r'd:\rks\s3\kanopus_missed\1159_PMS'
folder_out = r'e:\rks\kanopus_dymka\1159'
correct_vals = [20, 21, 22, 3]

xls_dict = xls_to_dict(xls_path)
raster_files = folder_paths(raster_data_path,1,'tif')

for folder in xls_dict:
    test = re.search('[0-9]', xls_dict[folder].get('mark'))
    if test:
        test = int(test.group())
        id = xls_dict[folder].get('id')
        if id:
            test = int(test)
            proc = process().input(folder)
            for ascene in proc.scenes:
                for file in raster_files:
                    if split3(file)[1]==id:
                        if IntersectRaster(file, ascene.datamask()):
                            folder_name = os.path.split(path_in)
                            copydir(folder, folder_out)
                            shutil.copyfile(file, fullpath(r'%s\%s\%s.tif' % (folder_out, folder_name, id)))
                            print('Folder copyied: %s' % id)
                            continue
                        else:
                            print('Raster mismatch: %s' % id)
        else:
            print('Incorrect mark: %s - %i' % (id, test))