from geodata import *

folder = r''

files = folder_paths(folder,1,'tif')

check_list = []

for file in files:
    res = StripRaster(file, compress='DEFLATE')
    if res==0:
        checklist.append(split3(file)[1])

if check_list:
    with open(fullpath(folder,'stripped.txt'),'w') as txt:
        txt.write('\n'.join(check_list))