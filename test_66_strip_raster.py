from geodata import *

folder = r'd:\rks\destrip_test\ETRIS.RP1.GTNL1.4949.5.0.2014-05-14.L0.NTSOMZ_MSK.NTSOMZ_MSK'

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