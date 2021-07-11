from geodata import *

img_in = r'e:\rks\razmetka\set085__20210705__resurs_kshmsa_vr_ms_clouds\images'
msk_in = r'e:\test\tiles'

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

def TileImage(img_in, msk_data):
    del_list = []
    for file in folder_paths(img_in, 1, 'tif'):
        folder, name, tif = split3(file)
        if FindAny(name, ['_red', 'green', '_blue', '_nir', '_nir1', '_nir2'], False):
            id = '_'.join(name.split('_')[:-1])
        else:
            id = name
        print(id)
        if id in msk_data:
            for grn in msk_data[id]:
                msk = msk_data[id][grn]
                name_out = '%s.GRN%s' % (name, grn)
                img_out = fullpath(folder, name_out, 'tif')
                BackMask(msk, file, img_out)
                print('MASKED: %s' % name_out)
        del_list.append(name)
    return del_list

msk_data = GetMaskOut(msk_in)
del_list = TileImage(img_in, msk_data)

scroll(del_list, header='Raster to delete:')
