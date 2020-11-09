from geodata import *

folder = r'\\172.21.195.215\thematic\products\s3\resursp'

files = folder_paths(folder,1,'tif')

checklist = []

for file in files:
    res = StripRaster(file, compress='DEFLATE')
    if res==0:
        name = split3(file)[1]
        print('File stripped: %s' % name)
        checklist.append(name)

if checklist:
    with open(fullpath(folder,'stripped.txt'),'w') as txt:
        txt.write('\n'.join(checklist))