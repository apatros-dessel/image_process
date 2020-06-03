from geodata import *

path_in = r'\\tt-nas-archive\NAS-Archive-2TB-4\resursp_grn'
path_out = r'\\tt-nas-archive\NAS-Archive-2TB-4\resursp_grn_ql'

img_list = folder_paths(path_in, 1, 'tif')
print('%i images found' % len(img_list))
for i, img in enumerate(img_list):
    f, name, ext = split3(img)
    MakeQuickRGB(img, fullpath(path_out, name, ext))
    print('%1 Quicklook written: %s' % (i+1, name))