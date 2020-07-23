# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = r'\\172.21.195.2\FTP-Share'
path_cover = r'\\172.21.195.2\FTP-Share\ftp\fullcover_cover.json'

proc = process().input(path_in, imsys_list=['PLN','DG','SS'])

proc.GetCoverJSON(path_cover, add_path=True)
