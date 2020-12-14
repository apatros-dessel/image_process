# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'\\172.21.195.2\FTP-Share\ftp\Change_detection\Landsat-Sentinel\Siberia_Lena\training',
]
path_cover = r'e:\test\LS8_vector_cover.json'

proc = process().input(path_in)
scroll(flist(proc.scenes, lambda x: x.meta.id), lower=len(proc))

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
