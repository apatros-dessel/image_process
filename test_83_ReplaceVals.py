from geodata import *

pin = r'e:\rks\razmetka'
replace = {32767:0}
imgtype = 'IM4'
msktype = 'MCL'

class FolderDirs(dict):

    def __init__(self, folder, miss_tmpt=None):
        if os.path.exists(folder):
            for name in os.listdir(folder):
                path = fullpath(folder, name)
                if os.path.isdir(path):
                    if miss_tmpt:
                        if re.search(miss_tmpt, name):
                            continue
                    self[name] = path

def GetRasterPairs(path):
    pairs = {}
    files = folder_paths(path,1,'tif')
    for file in files:
        f,n,e = split3(file)
        nameparts = n.split('-')
        id = '-'.join(nameparts[1:])
        if id in pairs:
            pairs[id][nameparts[0]] = file
        else:
            pairs[id] = {nameparts[0]: file}
    return pairs

pin = list(FolderDirs(pin).values())

for path in pin:
    print(path)
    pairs = GetRasterPairs(path)
    for id in pairs:
        img = pairs[id].get(imgtype)
        msk = pairs[id].get(msktype)
        if (img and msk):
            msk_raster = gdal.Open(msk)
            msk_uniques = list(np.unique(msk_raster.ReadAsArray()))
            msk_raster = None
            if msk_uniques==[201]:
                print(id, msk_uniques)
                # CreateDataMask(img, msk, value=201, nodata=0, bandnum=1)
                # msk_raster = gdal.Open(msk)
                # msk_uniques = list(np.unique(msk_raster.ReadAsArray()))
                # msk_raster = None
                # print(id, msk_uniques)
            else:
                # print(msk_uniques)
                pass
        else:
            # print(img, msk)
            pass

# for file in files:
    # ReplaceValues(file, replace)
    # raster = gdal.Open(file)
    # uniques = np.unique(raster.ReadAsArray())
    # print(raster.GetRasterBand(1).GetNoDataValue(), uniques[0], uniques[-1], split3(file)[1])