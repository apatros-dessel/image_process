# import os
import shutil
from image_processor import *

path_list = [
    r'd:\kanopus_new\rgb\Samara',
    # r'd:\kanopus_new\rgb\Krym',
]

pms_path = r'e:\kanopus_new\pansharpened\Samara'

vector_path = r'd:\digital_earth\resurs-p_new\krym\report_102_2020_108_rp.geojson'

path_out = r'd:\export\samara'

if not os.path.exists(path_out):
    os.makedirs(path_out)

errors = []

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
        for end in ['RGB.tif']:
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
                geodata.copydeflate(pms_fullpath, fullpath(save_path, pms_name))
                print('File saved: {}'.format(basename))
            else:
                errors.append(pms_name)
                print('File not found: {}'.format(pms_fullpath))

scroll(errors, header='Errors while saving files:')
'''
for folder_path in folder_paths(path_out)[0][1:]:
    folder_full = os.path.split(folder_path)[1]
    folder = folder_full.replace('_obrez', '')[:-3]
    print(folder)
    # print('File saved: {}'.format(folder_full + '.json'))
    geodata.filter_dataset_by_col(vector_path, 'product_id', folder, path_out = fullpath(folder_path, folder_full, 'json'), unique_vals = False)
'''
