from geodata import *
# from razmetka import Pansharp

paths = [
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\PAN\shp_hand\shp_hand_&without_cloud_30_m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\PAN\shp_hand\shp_hand_clouds_surface_30_m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\PAN\shp_hand\shp_hand_water_30_m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_clouds\PAN\shp_hand\shp_hand_clouds_mountains_30_m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_surface\PAN\shp_hand\shp_hand_surface_mountains_30_m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_snow\PAN\shp_hand\shp_hand_thick_snow_30m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_snow\PAN\shp_hand\shp_hand_less_snow_30m',
    r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_snow\PAN\shp_hand\shp_hand_autumn_surface_30m',
]
img_list_path = r'e:\test\img_list.txt'
files_ = []
for path in paths:
    files = folder_paths(path,1,'shp')
    if files:
        files_.extend(files)

# scroll(files_, counts=True)

files = files_
names = flist(files, Name)
scroll(DictCounts({}, names))
fin_files = []
fin_names = []

if os.path.exists(img_list_path):
    with open(img_list_path) as txt:
        img_list = txt.read().split('\n')
else:
    img_list = folder_paths(r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton',1,'tif')
    with open(img_list_path, 'w') as txt:
        txt.write('\n'.join(img_list))
img_names = flist(img_list, Name)

for i, name in enumerate(names):
    if (name in img_names) or ((name+'_30m') in img_names):
        error = True
        for img, img_name in zip(img_list, img_names):
            if name == img_name:
                pix_size = abs(gdal.Open(img).GetGeoTransform()[-1])
                if abs((pix_size - 30)) <= 1:
                    # print('%s %f' % (name, pix_size))
                    if img_name in fin_names:
                        print('DUPLICATE: %s' % img_name)
                    else:
                        fin_files.append(img)
                        fin_names.append(img_name)
                        if 'surface_mountains' in files[i]:
                            copyfile(img, fullpath(r'e:\rks\razmetka_source\resurs_pan_30m\img_surface_mountains_30m', img_name, 'tif'))
                            print('WRITTEN: %s' % name)
                        error = False
                else:
                    # print('PIX_SIZE ERROR: %s' % name)
                    pass
            elif img_name.endswith('30m') and (name == img_name[:-4]):
                pix_size = abs(gdal.Open(img).GetGeoTransform()[-1])
                if abs((pix_size - 30)) <= 1:
                    # print('%s %f' % (name, pix_size))
                    if img_name in fin_names:
                        # print('DUPLICATE: %s' % img_name)
                        pass
                    else:
                        fin_files.append(img)
                        fin_names.append(img_name)
                        if 'surface_mountains' in files[i]:
                            copyfile(img, fullpath(r'e:\rks\razmetka_source\resurs_pan_30m\img_surface_mountains_30m', img_name, 'tif'))
                            print('WRITTEN: %s' % name)
                        error = False
                else:
                    print('PIX_SIZE ERROR: %s' % name)
        if error:
            print('ERROR: %s' % name)
    else:
        print('ABSENT ERROR: %s' % name)

print(len(names), len(fin_files))
# scroll(img_files, counts=True)
# scroll(exp_files, counts=True)



sys.exit()

data = {}
for file in files:
    name = Name(file)
    if '.PMS' in name:
        continue
    type = ('MS', 'PAN')['.PAN' in name]
    id = name.replace('.PAN','.MS')
    if id in data:
        data[id][type] = file
    else:
        data[id] = {type: file}
for id in data:
    pan_path = data[id].get('PAN')
    ms_path = data[id].get('MS')
    if not (None in (pan_path, ms_path)):
        pms_path = ms_path.replace('.MS','.PMS')
        if os.path.exists(pms_path):
            print('FILE EXISTS: %s' % pms_path)
        else:
            Pansharp(pan_path, ms_path, pms_path)
            # print('PANSHARPENED: %s' % Name(pms_path))
    else:
        print('ERROR: %s' % id)
