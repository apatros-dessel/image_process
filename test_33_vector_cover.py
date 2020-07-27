# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\PSB\Collect\clip_PSB_cad3_jul7_SkySatCollect_5c9fe7b6-dd76-46ec-bb2d-a8e969d18b26\files\SkySatCollect\20200707_114232_ssc8_u0001'
path_cover = r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\PSB\Collect\clip_PSB_cad3_jul7_SkySatCollect_5c9fe7b6-dd76-46ec-bb2d-a8e969d18b26\files\SkySatCollect\20200707_114232_ssc8_u0001\cover_test1.json'

proc = process().input(path_in, imsys_list=['PLN','DG','SS'])

proc.GetCoverJSON(path_cover, add_path=True, data_mask=True)
