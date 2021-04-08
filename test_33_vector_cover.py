# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'e:\rks\source\Ресурс_КШМСА\КШМСА-ВР_Восточный',
]
path_cover = r'e:\rks\source\Ресурс_КШМСА\КШМСА-ВР_Восточный\vector_cover.json'

proc = process().input(path_in)
scroll(flist(proc.scenes, lambda x: x.meta.id), lower=len(proc))

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
