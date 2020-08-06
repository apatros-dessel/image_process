# -*- coding: utf-8 -*-

from image_processor import *

pin = r'f:\DG'
# xmlpath = r'\\172.21.195.2\FTP-Share\ftp\images_order\DG_moved\012751643030_01\012751643030_01_P001_PSH\18NOV15075722-S2AS-012751643030_01_P001.XML'
pout = r'\\172.21.195.2\FTP-Share\ftp\images_order\DG_moved\move'
xls_path = r'd:\digital_earth\DG_cover_remove.xls'
json_path = r'd:\digital_earth\DG_no_doubles_del_filtered.json'

def cutoff(str1, str2):
    if str1.startswith(str2):
        return str1[len(str2):]
    else:
        raise Exception(str1)

def copy_dir(din, pout, delete=False):
    corner, foldername = os.path.split(din)
    folders, files = folder_paths(din)
    for folder in folders:
        short = cutoff(folder, corner)
        folderout = fullpath(pout, short)
        suredir(folderout)
    for file in files:
        short = cutoff(file, corner)
        fileout = fullpath(pout, short)
        if delete:
            shutil.move(file, fileout)
        else:
            shutil.copyfile(file, fileout)
    if delete:
        destroydir(din)

def MoveDGData(xmlpath, pout, delete=False):
    corner1 = get_corner_dir(xmlpath)
    corner2, foldername = os.path.split(corner1)
    proc = process().input(corner2)
    if len(proc)==1:
        copy_dir(corner2, pout, delete=delete)
    elif len(proc)>1:
        # suredir(tpout)
        corner3, folder_master = os.path.split(corner2)
        tpout = fullpath(pout, folder_master)
        if not os.path.exists(fullpath(corner2, 'GIS_FILES')):
            raise Exception(corner2)
            corner4, folder_master = os.path.split(corner3)
        copy_dir(corner1, tpout, delete=delete)
        copy_dir(fullpath(corner2, 'GIS_FILES'), tpout)
        for f in os.listdir(corner2):
            if os.path.isfile(fullpath(corner2, f)):
                shutil.copyfile(fullpath(corner2, f), fullpath(tpout, f))


# move_dir(r'\\172.21.195.2\FTP-Share\ftp\images_order\DG_moved\012751772180_01',
         # r'\\172.21.195.2\FTP-Share\ftp\images_order\DG_moved\test',
         # delete=True)

# MoveDGData(xmlpath, pout, delete=False)

exclude_paths = []

xls_keys = xls_to_dict(xls_path)
# scroll(xls_keys)
for path in xls_keys:
    if xls_keys[path]['remove'] in [1,True, u'ИСТИНА']:
        exclude_paths.append(path)

din, lin = geodata.get_lyr_by_path(json_path)
for feat in lin:
    if feat.GetField('del') in [1,'1']:
        exclude_paths.append(feat.GetField('path'))

exclude_names = flist(exclude_paths, os.path.basename)

final_paths = []

for file in folder_paths(pin,1):
    f, name = os.path.split(file)
    if name in exclude_names:
        final_paths.append(file)

scroll(final_paths)
with open(r'd:\digital_earth\destroy.txt','w') as txt:
    txt.write('\n'.join(final_paths))

print('Just do it?')
doit = input('')

for xmlpath in final_paths:
    MoveDGData(xmlpath, pout, delete=False)