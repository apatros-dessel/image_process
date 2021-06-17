from razmetka import *

xls_in = r'e:\rks\new_data\102_2021_1266\report_decan.xls'
folder_out = r'e:\rks\new_data\select_decan'

export_dict = {
    # '17': 'mountain_snow',
    # '1': 'mountain',
    # '19': 'mountain',
    # '15': 'mountain',
    # '7': 'snow',
    # '10': 'clouds',
    # '9': 'water',
    '110': 'mountain_clouds',
    '1110': 'mountain_clouds',
    '190': 'mountain_clouds',
}

bands = {
    'red': 1,
    'green': 2,
    'blue': 3,
    'nir': 4,
}

band_folders = [
    'mountain',
    'mountain_clouds',
    'mountain_snow',
    'water',
]

xls_dict = xls_to_dict(xls_in)

for folder_in in xls_dict:
    mark = str(int(xls_dict[folder_in]['mark']))
    if mark in export_dict:
        export_files = folder_paths(folder_in,1,'tif')
        if export_files:
            export_folder = r'%s/MS/%s' % (folder_out, export_dict[mark])
            suredir(export_folder)
            # bands_folder = r'%s/Bands/%s' % (folder_out, export_dict[mark])
            # suredir(bands_folder)
            for file in export_files:
                name = Name(file)
                copyfile(file, fullpath(export_folder, name, 'tif'))
                # for band in bands:
                    # SetImage(file, r'%s/%s_%s.tif' % (bands_folder, name, band), band_num=1, band_reposition=[bands[band]], overwrite=False)
                print('WRITTEN: %s %s' % (export_dict[mark], name))

for id in os.listdir(r'%s/MS' % (folder_out)):
    export_folder = r'%s/MS/%s' % (folder_out, id)
    bands_folder = r'%s/Bands/%s' % (folder_out, id)
    suredir(bands_folder)
    for file in folder_paths(export_folder,1,'tif'):
        name = Name(file)
        for band in bands:
            SetImage(file, r'%s/%s_%s.tif' % (bands_folder, name, band), band_num=1, band_reposition=[bands[band]], overwrite=False)
        print('WRITTEN: %s' % name)
