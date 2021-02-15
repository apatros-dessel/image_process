# -*- coding: utf-8 -*-

from image_processor import *

path_in = r'e:\rks\newfin\test'    # Путь к исходным данным
path_cover = r'e:\rks\newfin\test\DG_fullcover.json'   # Путь к  файлу покрытия .json

proc = process().input(path_in)

proc.GetCoverJSON(path_cover)
