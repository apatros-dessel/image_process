from geodata import *

source = r'e:\rks\rucode\fetsival\Images_composit\8_ch'
source_mask = r'e:\rks\rucode\fetsival\mask'
out = r'e:\rks\rucode\festival_fin'

folder_comp8 = r'%s\Images_composit\8_ch' % out
folder_comp3 = r'%s\Images_composit\3_ch' % out
folder_old = r'%s\Images\first_date' % out
folder_new = r'%s\Images\second_date' % out
folder_mask = r'%s\mask' % out

for folder in (folder_comp8, folder_comp3, folder_old, folder_new, folder_mask):
    suredir(folder)

def SplitKompositName(name):
    kan1, kan2 = name.split('KV')[1:3]
    return 'KV'+kan1, 'KV'+kan2

def GetNewName(kan, num):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = kan.split('_')
    num2, scn, type, lvl = ending.split('.')
    scn_num = scn.replace('SCN0', 'SCN')
    return '%s_%s_%s_UN%s' % (satid, date, scn_num, num)

def KanopusRename(names):
    result = OrderedDict()
    for i, name in enumerate(names):
        kan1, kan2 = SplitKompositName(name)
        new_name1 = GetNewName(kan1, 2*i+1)
        new_name2 = GetNewName(kan2, 2*i+2)
        new_kompname = '%s__%s' % (new_name1, new_name2)
        result[name] = (new_kompname, new_name1, new_name2)
    return result

comp_files = folder_paths(source,1,'tif')
comp_names = flist(comp_files, Name)
mask_files = folder_paths(source_mask,1,'tif')
mask_names = flist(mask_files, Name)
rename = KanopusRename(comp_names)
for name, file in zip(comp_names, comp_files):
    new_kompname, new_name1, new_name2 = rename[name]
    new_file = fullpath(folder_comp8, new_kompname, 'tif')
    copyfile(file, new_file)
    SaveRasterBands(new_file, [1,2,3,4], fullpath(folder_old,new_name1,'tif'), options={'compress':'DEFLATE'}, overwrite=False)
    SaveRasterBands(new_file, [5,6,7,8], fullpath(folder_new,new_name2,'tif'), options={'compress': 'DEFLATE'}, overwrite=False)
    SaveRasterBands(new_file, [6,1,7], fullpath(folder_comp3,new_kompname+'__3CH','tif'), options={'compress': 'DEFLATE'}, overwrite=False)
    if name in mask_names:
        copyfile(mask_files[mask_names.index(name)], fullpath(folder_mask,new_kompname,'tif'))
    print('WRITTEN: %s' % new_kompname)

for name in rename:
    line = rename[name]
    new_line = OrderedDict()
    new_line['first_date'] = line[1]
    new_line['second_date'] = line[2]
    new_line['composit_8ch'] = line[0]
    new_line['composit_3ch'] = line[0]+'__3CH'
    rename[name] = new_line

dict_to_xls(fullpath(out, 'RucodeRenameTable.xls'), rename)