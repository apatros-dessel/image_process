from image_processor import *

paths = [
    r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\Krasnoyarsk best',
    r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\Krasnoyarsk best2',
    r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\Krasnoyarsk_best3',
    r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\Krasnoyarsk_best4',
    r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\Krasnoyarsk_best5',
    r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\Krasnoyarsk_best6',
]
txt_path = r'e:\rks\source\best_region82_check_QL.txt'

pin0 = r'\\172.21.195.2\FTP-Share\ftp\images\region82'
zero_paths = folder_paths(pin0,1,'tif')
zero_folders = flist(zero_paths,os.path.dirname)
zero_names = flist(zero_paths,os.path.basename)

pout = r'\\172.21.195.2\FTP-Share\ftp\images\region82_cover_fin.json'

filter_names_list = []
if txt_path is None:
    for pin in paths:
        filter_paths = folder_paths(pin,1,'tif')
        folder_names = flist(filter_paths, os.path.basename)
        for name in folder_names:
            if not name in filter_names_list:
                filter_names_list.append(name)
else:
    with open(txt_path) as txt:
        filter_names_list = txt.read().split('\n')

print(len(filter_names_list))
scroll(zero_names)

input_folder_list = []
for i, name in enumerate(zero_names):
    if name in filter_names_list:
        input_folder_list.append(zero_folders[i])

print(len(input_folder_list))

proc = process().input(input_folder_list, imsys_list=['RSP'], skip_duplicates=False)
proc.GetCoverJSON(pout)

