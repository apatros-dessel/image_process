# -*- coding: utf-8 -*-

import sys
from image_processor import *
from shutil import copyfile

path_in = FolderDirs(r'y:\\').values()
path_out = r'\\172.21.195.2\thematic\Sadkov_SA\covers\natarova_kanopus'
suredir(path_out)

for path in path_in:
    try:
        path_cover = fullpath(path_out, os.path.split(path)[1], 'json')
        if os.path.exists(path_cover):
            print('FILE_EXISTS: %s' % path_cover)
        else:
            proc = process().input(path, imsys_list = ['KAN'], skip_duplicates = False)
            # print(len(proc))
            # sys.exit()
            if len(proc)>0:
                #scroll(flist(proc.scenes, lambda x: x.meta.id), counts=True
                proc.GetCoverJSON(path_cover, add_path=True, cartezian_area=False, data_mask=False)
                print('FINISHED: %s' % path_cover)
            else:
                print('SKIPPED: %s' %  os.path.split(path)[1])
    except e:
        print('ERROR PROCESSING: %s %s' % (path, e))