from geodata import *

folders = FolderDirs(r'\\172.21.195.2\thematic\!razmetka\Meteor_KMSS\MS\img')
total_area = OrderedDict()
for name in folders:
    # if not name.startswith('set013'):
        # continue
    folder = folders[name]
    if not name in total_area:
       img_area = folder #+ r'\images'
       files = folder_paths(img_area,1,'tif')
       if files:
           sum = 0
           for file in files:
               sum += RasterDataArea(file)
           total_area[name] = {'area': sum/10**6}
           print('%s %i = %f' % (name, len(files), sum/10**6))
dict_to_xls(r'e:\rks\razmetka\areas.xls', total_area)