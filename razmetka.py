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
            path = fullpath(folder, name)
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
            path = fullpath(folder, name)
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
        return self

    def Fill(self, datacat):
        datacats = globals()['datacats']
        if datacat in datacats:
            datacatpath = (r'%s/%s/%s' % (self.corner, datacat, self.subtype)).rstrip(r'\/')
            if os.path.exists(datacatpath):
                self[datacat] = {}
                WriteLog('NEW SubtypeIndex %s %s %s' % (self.corner, self.subtype, datacat))
                files = FolderFiles(datacatpath, miss_tmpt='&', type=datacats[datacat])
                for name in files:
                    if not name in self[datacat]:
                        datapath = files[name]
                        self[datacat][name] = datapath
                        WriteLog('NEW SubtypeIndex %s %s %s %s %s' % (self.corner, self.subtype, datacat, name, datapath))
        else:
            print('WRONG DATACAT: %s' % datacat)

    def __len__(self):
        val = 0
        for datacat in self:
            val = max(val, len(self[datacat]))
        return val

    def __bool__(self):
        return bool(len(self))


class MaskTypeFolderIndex:

    def __init__(self, corner):
        self.corner = corner
        self.bandclasses = {}
        self.subtypes = {}
        self.FillMaskBandclasses()
        self.FillMaskSubtypes()

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
            datacatpath = r'%s/%s' % (bandclasspath, 'img')
            subtypedirs = FolderDirs(datacatpath, miss_tmpt='&')
            if subtypedirs is not None:
                subtypes.update(subtypedirs)
        for subtype in subtypes.keys():
            self.subtypes[subtype] = {}
            for bandclass in self.bandclasses:
                subtype_index = MaskSubtypeFolderIndex().FillFromDisk(self.bandclasses[bandclass], subtype)
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
        # scroll(full_imgs, header=subtype)
        if full_imgs:
            suredir(r'%s\BANDS\img\%s' % (self.corner, subtype))
            suredir(r'%s\BANDS_nir\img\%s' % (self.corner, subtype))
            for name in full_imgs:
                file = full_imgs[name]
                id = os.path.splitext(name)[0]
                for num, channel in zip((1,2,3),('red','green','blue')):
                    img_out = r'%s\BANDS\img\%s\%s_%s.tif' % (self.corner, subtype, id, channel)
                    SetImage(file, img_out, band_num=1, band_reposition=[num], overwrite=False)
                nir_out = r'%s\BANDS_nir\img\%s\%s_nir.tif' % (self.corner, subtype, id)
                SetImage(file, nir_out, band_num=1, band_reposition=[4], overwrite=False)
                print('BANDS WRITTEN: %s' % id)
        else:
            print('FULL IMAGE DATA NOT FOUND: %s' % subtype)

    def SavePanData(self, subtype=''):
        ms_imgs = self.Images(subtype, 'MS')
        if ms_imgs:
            pan_folder = r'%s\PAN\img\%s' % (self.corner, subtype)
            suredir(pan_folder)
            for name in ms_imgs:
                ms_id =  os.path.splitext(name)[0]
                pan_id = ms_id.replace('.MS','.PAN')
                UploadKanopusFromS3(pan_id, pan_folder)

    def SavePmsData(self, subtype=''):
        ms_imgs = self.Images(subtype, 'MS')
        if ms_imgs:
            pms_folder = r'%s\PMS\img\%s' % (self.corner, subtype)
            suredir(pms_folder)
            for name in ms_imgs:
                ms_id = os.path.splitext(name)[0]
                pms_id = ms_id.replace('.MS', '.PMS')
                l = UploadKanopusFromS3(pms_id, pms_folder)
                if l==0:
                    # self.Pansharp(subtype, pms_id)
                    print('SCENE NOT FOUND: %s' % pms_id)

    def GetScenePathFromID(self, subtype, kan_id):
        type = GetKanTypeFromID(kan_id)
        kan_path = r'%s\%s\img\%s\%s.tif' % (self.corner, type, subtype, kan_id)
        if os.path.exists(kan_path):
            return kan_path
        else:
            l = UploadKanopusFromS3(kan_id, os.path.dirname(kan_path))
            if l==1:
                return kan_path
            elif l>1:
                return r'%s\%s\img\%s\%s_1.tif' % (self.corner, type, subtype, kan_id)
            else:
                # print('SCENE NOT FOUND: %s' % kan_id)
                pass

    def Pansharp(self, subtype, pms_id):
        pms_path = self.GetScenePathFromID(subtype, pms_id)
        if pms_path:
            return pms_path
        ms_path = self.GetScenePathFromID(subtype, pms_id.replace('.PMS','.MS'))
        pan_path = self.GetScenePathFromID(subtype, pms_id.replace('.PMS','.PAN'))
        if ms_path and pan_path:
            command = r'python py2pci_pansharp.py %s $s %s -d TRUE' % (pan_path, ms_path, pms_path)
            os.system(command)
            return self.GetScenePathFromID(subtype, pms_id)
        else:
            print('CANNOT GET SOURCE DATA FOR PANSHARPENING: %s' % pms_id)

def GetKanTypeFromID(kan_id):
    if '.MS' in kan_id:
        return 'MS'
    elif '.PAN' in kan_id:
        return 'PAN'
    elif '.PMS' in kan_id:
        return 'PMS'

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
    if band_num > realBandNum:
        print('Not enough bands for: %s - got %i, need %i' % (img_in, realBandNum, band_num))
        raise Exception
    elif band_num < realBandNum:
        return True, band_num
    else:
        for i in range(1, band_num + 1):
            band = raster.GetRasterBand(i)
            if (band.DataType!=3) or (band.GetNoDataValue()!=0):
                return True, band_num
        return False, band_num

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

def UploadKanopusFromS3(kan_id, pout):
    folder = tempname()
    command = r'''gu_db_query -w "source='kanopus' and hashless_id='%s'" -d %s''' % (kan_id, folder)
    os.system(command)
    files = folder_paths(folder, 1, 'tif')
    l = len(files)
    if l == 1:
        shutil.copyfile(files[0], fullpath(pout, kan_id, 'tif'))
        print('WRITTEN: %s' % kan_id)
    elif l == 0:
        print('SCENE DATA NOT FOUND: %s' % kan_id)
    else:
        print('MULTIPLE SCENES FOUND FOR: %s - %i scenes' % (kan_id, l))
        for i, file in enumerate(files):
            shutil.copyfile(files[0], fullpath(pout, '%s_%i' % (kan_id, i+1), 'tif'))
    destroydir(folder)
    return l