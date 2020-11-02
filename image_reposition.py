# import os
import shutil, time
from image_processor import *

path_list = [
    r'e:\planet_rgb',
    # r'd:\kanopus_new\rgb\Samara',
    # r'd:\resursp_new\rgb\Krym',
]

pms_path = r'e:\kanopus_new\pansharpened\Krym'

vector_path_old = r'E:/test/Tver_Planet_cover.json'
vector_path = r'C:/Users/admin/Desktop/planet_error.geojson'

path_out = r'd:\export\planet\tver'

if not os.path.exists(path_out):
    os.makedirs(path_out)

errors = []
'''
for path in path_list:
    files = folder_paths(path, files=True, extension='tif')
    # scroll(files)
    for file in files:
        basename = os.path.split(file)[1]
        for end in [
            # 'QL.tif', 'IMG.tif', '_obrez.QL.tif', '_obrez.IMG.tif'
        ]:
            if basename.endswith(end):
                id = basename.replace(end, '')
                save_path = fullpath(path_out, id)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                shutil.copyfile(file, fullpath(save_path, basename))
                print('File saved: {}'.format(basename))
        for end in ['.tif']:
            pms_name = basename.replace('.RGB', '')
            # print(pms_name)
            pms_fullpath = fullpath(pms_path, pms_name)
            if os.path.exists(pms_fullpath):
                id = basename.replace(end, '')
                save_path = fullpath(path_out, id)
                if os.path.exists(fullpath(save_path, pms_name)):
                    print('File already exists: {}'.format(pms_name))
                    continue
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                if os.path.getsize(pms_fullpath) > 10**9:
                    print('Compressing raster data: {}'.format(pms_name))
                    geodata.copydeflate(pms_fullpath, fullpath(save_path, pms_name))
                else:
                    shutil.copyfile(pms_fullpath, fullpath(save_path, pms_name))
                print('File saved: {}'.format(basename))
            else:
                errors.append(pms_name)
                print('File not found: {}'.format(pms_fullpath))

scroll(errors, header='Errors while saving files:')
'''
for folder_path in folder_paths(path_out)[0][1:]:
    folder_full = os.path.split(folder_path)[1]
    folder = folder_full.replace('_obrez', '')
    # time.sleep(10)
    # print('File saved: {}'.format(folder_full + '.json'))
    ds_in, ds_out = geodata.get_lyr_by_path(vector_path)
    path_out = fullpath(folder_path, folder_full, 'json')
    if os.path.exists(path_out):
        if os.path.getsize(path_out) > 50:
            continue

    geodata.filter_dataset_by_col(vector_path_old, 'id', folder, path_out = fullpath(folder_path, folder_full, 'json'), unique_vals = True)
    if os.path.getsize(path_out) == 50:
        folder = folder_full.replace('_obrez', '')[:-14]
        geodata.filter_dataset_by_col(vector_path_old, 'id', folder, path_out = fullpath(folder_path, folder_full, 'json'), unique_vals = True)
        print('Written from new: {}'.format(folder))
    else:
        print('Written from old: {}'.format(folder))

