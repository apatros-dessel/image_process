# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = [
    r'\\172.21.195.2\FTP-Share\ftp\roslesinforg\balaganskoe\S3',
]
path_cover = r'\\172.21.195.2\FTP-Share\ftp\roslesinforg\balaganskoe\S3\SNT_сover.json'

proc = process().input(path_in)

scroll(proc.get_ids())
# for ascene in proc.scenes:
    # meta = ascene.meta
    # print('id: %s\ndatamask:%s' % (meta.id, meta.datamask))

proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)

sys.exit()

# path_in_list = obj2list(path_in)
# for i, path_in in enumerate(path_in_list):
    # path_cover_fin = path_cover.replace('.json','%s.json' % path_in[-8:].replace('\\','_'))
    #print(path_cover_fin)

