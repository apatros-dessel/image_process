# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'e:\rks\source\Ресурс КШМСА\KSHMSA_SR\selected_sr\RP1_16209_02_KSHMSA-SR_20160518_035512_035723.MS.RS',
]
path_cover = r'e:\rks\source\Ресурс КШМСА\KSHMSA_SR\selected_sr\RP1_16209_02_KSHMSA-SR_20160518_035512_035723.MS.RS\vector_cover.json'

proc = process().input(path_in)
scroll(flist(proc.scenes, lambda x: x.meta.id), lower=len(proc))

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
