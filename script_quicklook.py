# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'd:\Krym\!fin\rgb'
dir_out = r'd:\Krym\!fin\quicklook'

path_in_list = folder_paths(dir_in, files=True, extension='tif')
dir_out_3857 = fullpath(dir_out, '3857')
if not os.path.exists(dir_out_3857):
    os.makedirs(dir_out_3857)
dir_out_img = fullpath(dir_out, 'img')
if not os.path.exists(dir_out_img):
    os.makedirs(dir_out_img)

# scroll(path_in_list)

for i, path_in in enumerate(path_in_list):
    if path_in.endswith('.tif'):
        filename = os.path.split(path_in)[1]
        try:
            path_out = fullpath(dir_out_3857, filename)
            res = MakeQuicklook(path_in, path_out, 3857, pixelsize=30, overwrite=False)
            if res == 0:
                QuicklookImage(path_out, fullpath(dir_out_img, filename))
                print('{} File saved: {}'.format(i+1, filename))
            else:
                print('{} File not saved: {}'.format(i + 1, filename))
        except:
            print('{} File not saved: {}'.format(i+1, filename))