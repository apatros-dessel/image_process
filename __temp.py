from geodata import *

path = r'\\172.21.195.2\thematic\!projects\Rucode\images_fin\composits\8_ch'
out = r'e:\rks\source\kanopus_test\Rucode\composite\test\8_bands'
names = folder_paths(path,1,'tif')
source = r'e:\rks\source\kanopus_test\Rucode\source'
outxls = r'e:\rks\source\kanopus_test\Rucode\reproject\komposit_list.xls'


source_files = folder_paths(source,1,'tif')
report = OrderedDict()


sys.exit()
for file in names:
    name = split3(file)[1]
    basics = name.split('.L2')
    old = basics[0] + '.L2'
    new = basics[1] + '.L2'
    if 'RRG' in basics[2]:
        continue
    channels = [1,2,3,4,1,2,3,4]
    line = OrderedDict()
    for file in source_files:
        if old in file:
            line['old'] = old
        elif new in file:
            line['new'] = new
    if line.get('old') and line.get('new'):
        line['composit'] = name
        line['channels'] = '1,2,3,4,1,2,3,4'
        report[name] = line
    else:
        print('Wrong name: %s' % name)

dict_to_xls(outxls,report)
