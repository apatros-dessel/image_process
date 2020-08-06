# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\May\cut1',
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\May\cut2',
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\May\cut3',
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\Jun\cut1',
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\Jun\cut2',
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\Jun\cut3',
    r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\Jul\cut1',
]
path_cover = r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\planet_case1_сover_.json'

path_in_list = obj2list(path_in)
for i, path_in in enumerate(path_in_list):
    proc = process().input(path_in)
    path_cover_fin = path_cover.replace('.json','%s.json' % path_in[-8:].replace('\\','_'))
    #print(path_cover_fin)
    proc.GetCoverJSON(path_cover_fin, add_path=True, cartezian_area=False, data_mask=False)
