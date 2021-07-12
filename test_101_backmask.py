from razmetka import *

img_folder_out = r'e:\rks\razmetka\set090__20210706__resurs_kshmsa_vr_clouds_bands_nir2\images\resurs'
msk_in = r'e:\test\tiles'
img_tiles_folder = r'e:\test\tiles_img'
# img_in = r'e:\rks\razmetka\set087__20210706__resurs_kshmsa_vr_clouds_bands_green\images\resurs'
msk_folder_out = r'e:\rks\razmetka\set090__20210706__resurs_kshmsa_vr_clouds_bands_nir2\masks\full\resurs'
msk_match_folder = r'e:\test\basic'

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
        if FindAny(name, ['_red', '_green', '_blue', '_nir', '_nir1', '_nir2'], False):
            parts = name.split('_')
            id = '_'.join(parts[:-1])
            color = '_' + parts[-1]
        else:
            id = name
            color = ''
        # print(id)
        if id in msk_data:
            for grn in msk_data[id]:
                msk = msk_data[id][grn]
                img_name = '%s.GRN%s%s' % (id, grn, color)
                img_out = fullpath(folder, img_name, tif)
                if os.path.exists(img_out):
                    continue
                else:
                    # BackMask(msk, file, img_out)
                    # print(['', '_red', '_green', '_blue', '_nir1', '_nir2'].index(color))
                    # sys.exit()
                    RepairImage(msk, img_out, 1, band_order = [['', '_red', '_green', '_blue', '_nir1', '_nir2'].index(color)])
                    print('MASKED: %s' % img_name)
            delete(file)
            del_list.append(name)
    return del_list

def TileMask(msk_folder, msk_match_folder, msk_data):
    del_list = []
    msk_files = folder_paths(msk_folder,1,'tif')
    msk_match_folder = folder_paths(msk_match_folder,1,'tif')
    msk_match_names = flist(msk_match_folder, Name)
    # scroll(msk_files)
    # sys.exit()
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
                    msk_out = fullpath(folder, msk_name, tif)
                    if os.path.exists(msk_out):
                        continue
                    else:
                        copyfile(msk_data[id][grn], msk_out)
                        print('COPY MASK: %s' % name)
                delete(msk_in)
                del_list.append(name)
            else:
                print('RASTER MASK MISMATCH: %s' % name)
    return del_list

img_data = GetMaskOut(img_tiles_folder)
del_list = TileImage(img_folder_out, img_data)
scroll(del_list, header='Raster to delete:')

msk_data = GetMaskOut(msk_in)
del_list = TileMask(msk_folder_out, msk_match_folder, msk_data)
scroll(del_list, header='Mask to delete:')
