from tools import *
import shutil

path_pms = r'g:\rks\digital_earth\processed\kanopus\Tver\rgb'
path_source = r'f:\102_2020_126'
path_out = r'g:\rks\digital_earth\processed\kanopus\Tver\ms'

path_xls = r'G:\rks\digital_earth\selection\Tver_new.xls'
xls_names = xls_to_dict(path_xls).keys()

pms_list = folder_paths(path_pms, files=True, extension='tif')
ms_list = folder_paths(path_source, files=True, extension='tif')
suredir(path_out)

# for i, pms_fullpath in enumerate(pms_list):
for i, pms_file in enumerate(xls_names):
    # pms_folder, pms_file = os.path.split(pms_fullpath)
    ms_file = pms_file.replace('.PMS', '.MS')
    for ms_fullpath in ms_list:
        if ms_file in ms_fullpath:
            ms_folder, ms_file = os.path.split(ms_fullpath)
            shutil.copyfile(ms_fullpath, fullpath(path_out, ms_file))
            print('%i file written: %s' % (i+1, ms_file))
            break