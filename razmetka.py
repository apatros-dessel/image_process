from geodata import *

bandclasses = ('MS','PAN','PMS','BANDS','BANDS_nir')
datacats = {'img': ('tif'),
            'mask': ('tif'),
            'shp_auto': ('shp','json','geojson'),
            'shp_hand': ('shp', 'json','geojson'),
            'test_result': ('shp','json','geojson'),
            }
objidval = 0

def WriteLog(logstring, logpath = None):
    datestring = str(datetime.now()).replace(' ', '_').replace(':', '-')
    datelogstring = '%s %s\n' % (datestring, logstring)
    if logpath is None:
        logpath = globals().get('logpath')
        if logpath is None:
            logpath = tempname('txt')
            globals()['logpath'] = logpath
    style = ('w', 'a')[os.path.exists(logpath)]
    with open(logpath, style) as txt:
        txt.write(datelogstring)

class FolderDirs(dict):

    def __init__(self, folder, miss_tmpt=None):
        for name in os.listdir(folder):
            path = folder_paths(folder, name)
            if os.path.isdir(path):
                if miss_tmpt:
                    if re.search(miss_tmpt, name):
                        continue
                self[name] = path


class FolderFiles(dict):

    def __init__(self, folder, miss_tmpt=None, type=None):
        if type is not None:
            typelist = obj2list(type)
        else:
            typelist = None
        for name in os.listdir(folder):
            path = folder_paths(folder, name)
            if os.path.isfile(path):
                if typelist is not None:
                    for _type in typelist:
                        if name.lower().endswith(_type):
                            self[name] = path
            elif miss_tmpt:
                if re.search(miss_tmpt, name):
                    new_paths = FolderFiles(path)
                    if new_paths:
                        for new_name in new_paths:
                            self[r'%s/%s' % (name, new_name)] = new_paths[new_name]


class MaskSubtypeFolderIndex(dict):

    def __init__(self):
        self.corner = None
        self.subtype = None

    def FillFromDisk(self, corner, subtype):
        self.corner = corner
        self.subtype = subtype
        WriteLog('NEW SubtypeIndex %s %s' % (corner, subtype))
        datacats = globals()['datacats']
        for datacat in datacats:
            self.Fill(datacat)

    def Fill(self, datacat):
        datacats = globals()['datacats']
        if datacat in datacats:
            datacatpath = r'%s/%s/%s' % (self.corner, datacat, self.subtype).rstrip(r'\/')
            if os.path.exists(datacatpath):
                self[datacat] = {}
                WriteLog('NEW SubtypeIndex %s %s %s' % (self.corner, self.subtype, datacat))
                for name in FolderFiles(datacatpath, miss_tmpt='&', type=datacats[datacat]):
                    if not name in self[datacat]:
                        datapath = datacatpath[name]
                        self[datacat][name] = datapath
                        WriteLog('NEW SubtypeIndex %s %s %s' % (self.corner, self.subtype, datacat, name, datapath))
        else:
            print('WRONG DATACAT: %s' % datacat)

    def __len__(self):
        return max(flist(self.values(), len))

    def __bool__(self):
        return bool(len(self))


class MaskTypeFolderIndex:

    def __init__(self, corner):
        self.corner = corner
        self.bandclasses = {}
        self.subtypes = {}
        self.FillMaskBandclasses()
        self.FillMaskSubtypes()

        mask_type_dirs = FolderDirs(corner)
        for datacat in globals()['datacats']:
            if not datacat in mask_type_dirs:
                print('WRONG DATACAT: %s' % datacat)
                return None

    def FillMaskBandclasses(self):
        bandclasses = globals()['bandclasses']
        for bandclass in bandclasses:
            bandclasspath = r'%s/%s' % (self.corner, bandclass)
            if os.path.exists(bandclasspath):
                self.bandclasses[bandclass] = bandclasspath

    def FillMaskSubtypes(self):
        datacats = globals()['datacats']
        subtypes = {'': None}
        for bandclass in self.bandclasses:
            bandclasspath = self.bandclasses[bandclass]
            for datacat in datacats:
                datacatpath = r'%s/%s' % (bandclasspath, datacat)
                subtypedirs = FolderDirs(datacatpath, miss_tmpt='&')
                if subtypedirs is not None:
                    subtypes.update(subtypedirs)
        for subtype in subtypes.keys():
            self.subtypes[subtype] = {}
            for bandclass in self.bandclasses:
                subtype_index = MaskSubtypeFolderIndex(self.bandclasses[bandclass], subtype)
                if subtype_index:
                    self.subtypes[subtype][bandclass] = subtype_index

    def Subtype(self, subtype):
        if subtype in self.subtypes:
            return self.subtypes[subtype]
        else:
            print('SUBTYPE NOT FOUND: %s' % subtype)

    def Images(self, subtype='', bandclass='MS'):
        subtype_dict = self.Subtype(subtype)
        if subtype_dict:
            if bandclass in subtype_dict:
                if 'img' in subtype_dict[bandclass]:
                    return subtype_dict[bandclass]['img']
                else:
                    print('MS IMG FOLDER NOT FOUND: %s' % subtype)
            else:
                print('MS DATA NOT FOUND: %s' % subtype)

    def SaveBandsSeparated(self, subtype=''):
        full_imgs = self.Images(subtype, 'MS')
        if full_imgs:
            for name in full_imgs:
                file = full_imgs[name]
                for num, channel in zip((1,2,3),('red','blue','nir')):
                    img_out = r'%s\BANDS\%s\%s_%s.tif' % (self.corner, subtype, name, channel)
                    SetImage(file, img_out, band_num=1, band_reposition=[num], overwrite=False)
                nir_out = r'%s\BANDS_nir\%s\%s_nir.tif' % (self.corner, subtype, name)
                SetImage(file, nir_out, band_num=1, band_reposition=[4], overwrite=False)
        else:
            print('FULL IMAGE DATA NOT FOUND: %s' % subtype)

# Записать изображение, проверяя корректность его формата
# Если overwrite==False, то изображения в корректном формате пропускаются
def SetImage(img_in, img_out, band_num=1, band_reposition=None, multiply=None, neuro_check=False, overwrite = False):
    if neuro_check:
        neuro = split3(img_out)[1]
    else:
        neuro = None
    if os.path.exists(img_out):
        repair, counter = CheckImage(img_out, neuro=neuro, band_num=band_num)
        if not (repair or overwrite):
            return img_out
    if os.path.exists(img_in):
        repair, counter = CheckImage(img_in, neuro=neuro, band_num=band_num)
    else:
        print('Path not found: %s' % img_in)
        return 'ERROR: Source file not found'
    if repair:
        return RepairImage(img_in, img_out, counter, band_order = band_reposition, multiply = multiply)
    else:
        shutil.copyfile(img_in, img_out)
        return img_out

# Check if the image needs repair
def CheckImage(img_in, neuro = None, band_num = 1):
    raster = gdal.Open(img_in)
    realBandNum = raster.RasterCount
    if neuro:
        img_type = neuro.split('__')[0].split('-')[0]
        if re.search(r'^IM\d+$', img_type):
            band_num = int(img_type[2:])
        elif re.search(r'IM[RGBN]$', img_type):
            band_num = 1
        elif re.search(r'IMCH\d+$', img_type):
            band_num = int(img_type[4:])
    counter = min((band_num, realBandNum))
    if band_num > realBandNum:
        print('Not enough bands for: %s - got %i, need %i' % (img_in, realBandNum, band_num))
        raise Exception
    elif band_num < realBandNum:
        print('Band count mismatch for: %s - got %i, need %i' % (img_in, realBandNum, band_num))
        return True, counter
    counter = min((band_num, realBandNum))
    for i in range(1, counter + 1):
        band = raster.GetRasterBand(i)
        if band.DataType != 3 or band.GetNoDataValue() != 0:
            return True, counter
    return False, counter

# Записать растр снимка в установленном формате
def RepairImage(img_in, img_out, count, band_order=None, multiply = None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':3, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(band_order, range(1, count+1)):
        init_band = raster.GetRasterBand(bin)
        arr_ = init_band.ReadAsArray()
        init_nodata = init_band.GetNoDataValue()
        if init_nodata is None:
            init_nodata=0
            uniques, counts = np.unique(arr_, return_counts=True)
            total_sum = np.sum(counts)
            if counts[0]/total_sum>0.01:
                init_nodata=uniques[0]
            elif counts[-1]/total_sum>0.01:
                init_nodata=uniques[-1]
        arr_[arr_==init_nodata] = 0
        if multiply is not None:
            if bin in multiply.keys():
                arr_ = arr_ * multiply[bin]
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out
