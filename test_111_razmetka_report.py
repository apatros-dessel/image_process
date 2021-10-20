from script_razmetka_2 import *

folders = FolderDirs(r'd:\rks\razmetka').values()
# folders = [r'e:\rks\razmetka\!set038__20201218__water_landsat']

meta_folder = r'\\172.21.195.2\thematic\Sadkov_SA\code\razmetka_params'
sattelites = xls_to_dict(fullpath(meta_folder, 'sattelites.xls'))
legend = xls_to_dict(fullpath(meta_folder, 'legend.xls'))
report_col_order = ['r', 'v', 'img_out', 'msk_out', 'x_pix_count', 'y_pix_count', 'x_pix_size', 'y_pix_size',
                        'data_min', 'data_max', 'matrix_check', 'bits_exceed', 'msk_values']

for folder in folders:
    Report(folder)
    print('FINISHED: ' + os.path.split(folder)[1])