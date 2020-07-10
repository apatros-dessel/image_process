# -*- coding: utf-8 -*-

from image_processor import *

path_in = r'\\172.21.195.2\FTP-Share\ftp\images_order\images\DG'    # Путь к исходным данным
path_cover = r'e:\rks\razmetka\DG_fullcover.json'   # Путь к  файлу покрытия .json

proc = process().input(path_in)

proc.GetCoverJSON(path_cover)
