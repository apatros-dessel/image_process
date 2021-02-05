# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'\\172.21.195.2\thematic\Sadkov_SA\kanopus_dymka\102_2020_1339',
]
path_cover = r'\\172.21.195.2\thematic\Sadkov_SA\kanopus_dymka\102_2020_1339\vector_cover.json'

proc = process().input(path_in)
scroll(flist(proc.scenes, lambda x: x.meta.id), lower=len(proc))

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
