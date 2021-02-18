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
                self.subtypes[bandclass] = {}

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
        for bandclass in self.bandclasses:
            for subtype in subtypes.keys():
                subtype_index = MaskSubtypeFolderIndex(self.corner, subtype)
                if subtype_index:
                    self.subtypes[bandclass][subtype] = subtype_index

# Записать растр снимка в установленном формате
def RepairImage(img_in, img_out, count, band_order=None, multiply = None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':3, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(band_order, range(1, count+1)):
        arr_ = raster.GetRasterBand(bin).ReadAsArray()
        o = np.unique(arr_)[0]
        arr_[arr_ == o] = 0
        if multiply is not None:
            if bin in multiply.keys():
                arr_ = arr_ * multiply[bin]
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out
