# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = r'f:\102_2020_126'
path_cover = r'g:\rks\DE\processed\kanopus\Tver\102_2020_126_fullcover.json'
# path_quick = r'g:\rks\DE\SOUR\KAN\102_2020_325\quicklook'

proc = process().input(path_in)

# id_list = xls_to_dict(r'G:\rks\digital_earth\selection\Tver_new.xls').keys()

# proc_new = proc.filter_ids(id_list)

proc.GetCoverJSON(path_cover)

sys.exit()

suredir(path_quick)

for ascene in proc.scenes:
    quick = ascene.quicklook()
    if quick is not None:
        basename = os.path.basename(quick)
        copyfile(quick, fullpath(path_quick, basename))