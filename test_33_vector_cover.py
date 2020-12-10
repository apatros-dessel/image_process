# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'\\172.21.195.2\FTP-Share\ftp\image_exchange\sentinel\atmosphere\images',
]
path_cover = r'\\172.21.195.2\FTP-Share\ftp\image_exchange\sentinel\atmosphere\images\vector_cover.json'

proc = process().input(path_in)

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
