from geodata import *

folder_in = r'e:\rks\rucode\festival_fin\Images_composit\8_ch'
folder_out = r'e:\rks\rucode\festival_fin\mask_fin'

suredir(folder_out)

def GetPairs(folder_in):
    pairs = {}
    tif_files = folder_paths(folder_in,1,'tif')
    tif_names = flist(tif_files, Name)
    shp_files = folder_paths(folder_in,1,'shp')
    shp_names = flist(shp_files, Name)
    for i, name in enumerate(tif_names):
        if name in shp_names:
            pairs[name] = {'r': tif_files[i], 'v': shp_files[shp_names.index(name)]}
            print('WRITTEN: %s' % name)
        else:
            print('SHP NOT FOUND: %s' % name)
    return pairs

pairs = GetPairs(folder_in)
# scroll(pairs)

for name in pairs:
    RasterizeVector(pairs[name]['v'], pairs[name]['r'], fullpath(folder_out, name, 'tif'),
                    burn_value = 1, data_type = 1, value_colname = None, value_colname_sec = None, filter_nodata = True, compress = 'DEFLATE', overwrite=False)
