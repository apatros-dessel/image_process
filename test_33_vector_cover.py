# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'\\172.21.195.2\thematic\Sarychev_EU\Sentinel\S2B_MSIL2A_20180622T085559_N9999_R007_T37VCE_20210210T095416.SAFE',
]
path_cover = r'\\172.21.195.2\thematic\Sarychev_EU\Sentinel\S2B_MSIL2A_20180622T085559_N9999_R007_T37VCE_20210210T095416.SAFE\vector_cover.json'

proc = process().input(path_in)
scroll(flist(proc.scenes, lambda x: x.meta.id), lower=len(proc))

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
