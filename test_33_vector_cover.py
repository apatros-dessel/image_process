# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'd:\terratech\Voshod\edit',
]
path_cover = r'd:\terratech\Voshod\fin\vector_cover.json'

proc = process().input(path_in)
#scroll(flist(proc.scenes, lambda x: x.meta.id), counts=True)

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
