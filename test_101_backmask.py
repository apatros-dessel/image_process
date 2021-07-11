from razmetka import *

img_folder_out = r'e:\rks\razmetka\set085__20210705__resurs_kshmsa_vr_ms_clouds\images'
msk_in = r'e:\test\tiles'
img_in = r''
msk_folder_out = r''
msk_match_folder = r''

def GetMaskOut(msk_in):
    final = OrderedDict()
    for file in folder_paths(msk_in, 'tif'):
        name = Name(file)
        id, grn = name.split('.GRN')
        if id in final:
            final[id][grn] = file
        else:
            final[id] = {grn: file}
    return final

def TileImage(img_folder, msk_data):
    del_list = []
    for file in folder_paths(img_folder, 1, 'tif'):
        folder, name, tif = split3(file)
        if FindAny(name, ['_red', 'green', '_blue', '_nir', '_nir1', '_nir2'], False):
            id = '_'.join(name.split('_')[:-1])
        else:
            id = name
        # print(id)
        if id in msk_data:
            for grn in msk_data[id]:
                msk = msk_data[id][grn]
                name_out = '%s.GRN%s' % (name, grn)
                img_out = fullpath(folder, name_out, 'tif')
                # BackMask(msk, file, img_out)
                RepairImage(msk, img_out, 1, band_order = [1])
                print('MASKED: %s' % name_out)
        del_list.append(name)
    return del_list

def TileMask(msk_folder, msk_match_folder, msk_data, msk_out_folder):
    del_list = []
    msk_files = folder_paths(msk_folder,1,'tif')
    msk_match_folder = folder_paths(msk_match_folder,1,'tif')
    msk_match_names = flist(msk_match_folder, Name)
    for msk_in in msk_files:
        folder, name, tif = split3(msk_in)
        if FindAny(name, ['_red', 'green', '_blue', '_nir', '_nir1', '_nir2'], False):
            parts = name.split('_')
            id = '_'.join(parts[:-1])
            color = '_' + parts[-1]
        else:
            id = name
            color = ''
        if (id in msk_match_names) and (id in msk_data):
            if os.path.getsize(msk_in)==os.path.getsize(msk_match_folder[msk_match_names.index(id)]):
                for grn in msk_data[id]:
                    msk_name = '%s.GRN%s%s' % (id, grn, color)
                    msk_out = fullpath(msk_out_folder, name, tif)
                    copyfile(msk_data[id], msk_out)
                    print('COPY MASK: %s' % name)
                del_list.append(name)
            else:
                print('RASTER MASK MISMATCH: %s' % name)
    return del_list

msk_data = GetMaskOut(msk_in)
# del_list = TileImage(img_in, msk_data)
# del_list = TileMask(msk_folder, msk_match_folder, msk_data, msk_out_folder)

scroll(del_list, header='Raster to delete:')
