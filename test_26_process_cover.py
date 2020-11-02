# -*- coding: utf-8 -*-

from image_processor import *

# path = r'd:\digital_earth\kanopus_new\krym\KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.MS_666b82c6286dfde9d29e9f08f738a1fe66fbcf8c'
# proc = process().input(path)

def make_filelist_xls(folder, path2xls, extension=None):
    files = folder_paths(folder, files=1, extension=extension)
    if files is not None:
        export_dict = OrderedDict()
        for file in files:
            file_line = OrderedDict()
            file_line['basename'] = os.path.basename(file)
            export_dict[file] = file_line
        dict_to_xls(path2xls, export_dict)
        return 0
    else:
        return 1

path2folders_list = [
    # r'e:\kanopus_new\pansharpened\Krym',
    # r'd:\kanopus_new\quicklook\Samara\img',
    # r'd:\kanopus_new\quicklook\Tatarstan\img',
    # r'd:\kanopus_new\quicklook\Tver\img',
    # r'e:\planet_rgb',
]

path2xls_list = [
    # r'd:\digital_earth\kanopus_new\vector\krym_fin.xls',
    # r'd:\digital_earth\kanopus_new\vector\Samara_fin.xls',
    # r'd:\digital_earth\kanopus_new\vector\tatarstan.xls',
    # r'd:\digital_earth\kanopus_new\vector\Tver.xls',
    r'D:/digital_earth/planet/planet_cover_tver_full.xls',
]

vector_cover_in_list = [
    # r'd:\digital_earth\kanopus_new\krym\report_102_2020_116_kv.geojson',
    # r'd:\digital_earth\kanopus_new\samara\report_102_2020_180_kv.geojson',
    # r'd:\digital_earth\kanopus_new\tatarstan\report_102_2020_118_kv.geojson',
    # r'd:\digital_earth\kanopus_new\tver\report_102_2020_126_kv.geojson',
    r'D:/digital_earth/planet/planet_cover_tver_full.shp',
]
vector_cover_path_list = [
    # r'e:\test\cover_krym_fin.json',
    # r'e:\test\cover_samara_fin.json',
    # r'e:\test\cover_tatarstan.json',
    # r'e:\test\cover_tver.json',
    r'e:\test\cover_tver_planet_fin.json',
]

for folder, path2xls in zip(path2folders_list, path2xls_list):
    make_filelist_xls(folder, path2xls, 'tif')

for path2xls, vector_cover_in, vector_cover_path in zip(path2xls_list, vector_cover_in_list, vector_cover_path_list):

    xls_dict = xls_to_dict(path2xls)
    # fullpath_list = xls_dict.keys()
    fullpath_list = colfromdict(xls_dict, 'basename', listed=True)

    for i, id in enumerate(fullpath_list):
        fullpath_list[i] = id[:-7]

    scroll(fullpath_list)
    print(len(fullpath_list))

    geodata.filter_dataset_by_col(vector_cover_in, 'product_id', fullpath_list, path_out = vector_cover_path, unique_vals=True)
