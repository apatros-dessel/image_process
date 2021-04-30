from geodata import *

bandclasses = ('MS','PAN','PMS','BANDS','BANDS_nir')
datacats = {'img': ('tif'),
            'img_check': ('tif'),
            'mask': ('tif'),
            'shp_auto': ('shp','json','geojson'),
            'shp_hand': ('shp', 'json','geojson'),
            'test_result': ('shp','json','geojson'),
            }
band_params = {
    'red': [1, 'BANDS'],
    'green': [2, 'BANDS'],
    'blue': [3, 'BANDS'],
    'nir': [4, 'BANDS_nir'],
}
targets = {
    u'quarry': {'id': 'MQR', 'folder': 'mines', },
    u'water':    {'id': 'MWT', 'folder': 'water'},
    u'forest':     {'id': 'MFS', 'folder': 'forest'},
    u'change': {'id': 'MCHD', 'folder': 'change'},
    u'full':    {'id': 'MSK', 'folder': 'full'},
    u'svalki':  {'id': 'MWS', 'folder': 'svalki'},
    u'fields_grow': {'id': 'MFG', 'folder': 'fields_grow'},
    u'houses':    {'id': 'MBD', 'folder': 'houses'},
    u'TBO':     {'id': 'MWS', 'folder': 'wastes'},
    u'roads':  {'id': 'MRD', 'folder': 'roads'},
    u'gari':    {'id': 'MFR', 'folder': 'gari'},
    'clouds': {'id': 'MCL', 'folder': 'clouds'},
    'mist': {'id': 'MMI', 'folder': 'mist'},
}
codes = {
    1:  'карьеры (любые)',
    10: 'карьеры, без воды и растительности',
    11: 'карьеры, с растительностью, без воды',
    12: 'карьеры, с водой, без растительности',
    13: 'карьеры, с водой и растительностью',
    2:  'вскрытые грунты (любые)',
    20: 'вскрытые грунты, без воды и растительности',
    21: 'вскрытые грунты, с растительностью, без воды',
    22: 'вскрытые грунты, с водой, без растительности',
    23: 'вскрытые грунты, с водой и ратсительностью',
    24: 'свалки (отдельные маски для свалок с префиксом MDP)',
    25: 'полигоны ТБО',
    26: 'нарушенные земли',
    27: 'гольцы',
    3:  'площадки строительства (любые)',
    30: 'площадки строительства, без воды и растительности',
    31: 'площадки строительства, с растительностью, без воды',
    32: 'площадки строительства, с водой, без растительности',
    33: 'площадки строительства, с водой и растительностью',
    4:  'леса (любые)',
    41: 'лес на болоте',
    411:'широколиственные леса',
    41113:'широколиственные зрелые сомкнутые леса',
    41114:'широколиственные зрелые редкостойные леса',
    41123:'широколиственные молодые сомкнутые леса',
    41124:'широколиственные молодые редкостойные леса',
    412:'мелколиственные леса',
    41213:'мелколиственные зрелые сомкнутые леса',
    41214:'мелколиственные зрелые редкостойные леса',
    41223:'мелколиственные молодые сомкнутые леса',
    41224:'мелколиственные молодые редкостойные леса',
    42: 'светлохвойные леса',
    421:'лиственничники',
    42113:'лиственничники зрелые сомкнутые',
    42114:'лиственничники зрелые редкостойные',
    42123:'лиственничники молодые сомкнутые',
    42124:'лиственничники молодые редкостойные',
    422:'сосняки',
    42213:'сосняки зрелые сомкнутые',
    42214:'сосняки зрелые редкостойные',
    42223:'сосняки молодые сомкнутые',
    42224:'сосняки молодые редкостойные',
    43: 'темнохвойные леса',
    43013:'темнохвойные зрелые сомкнутые леса',
    43014:'темнохвойные зрелые редкостойные леса',
    43023:'темнохвойные молодые сомкнутые леса',
    43024:'темнохвойные молодые редкостойные леса',
    44: 'горельники (без детализации породного состава и интенсивности огня)',
    441:'горельники, пройденные верховым пожаром',
    442:'горельники, пройденные низовым пожаром',
    45: 'зарастание полей',
    5:  'здания (любые)',
    501:'застройка (по среднему и низкому разрешению)',
    51: 'жилые малоэтажные здания',
    52: 'жилые многоэтажные здания',
    53: 'промышленные, коммерческие, исторические и муниципальные здания',
    54: 'автодороги (любые)',
    541:'автодороги с покрытием',
    542:'автодороги грунтовые',
    55: 'железные дороги',
    6:  'болота',
    7:  'изменения (не используется, т.к. аналогичен 100)',
    8:  'травянистая растительность (луга, поля и т.д.)',
    81: 'поля',
    9:  'водные объекты (любые)',
    100:'изменения (любые)',
    101:'новые карьеры (любые)',
    102:'новые вскрытые грунты (любые)',
    103:'новые площадки строительства (любые)',
    140:'вырубка (любая)',
    141:'вырубка сплошная',
    142:'вырубка выборочная',
    143:'больной, высохший или сгоревший лес',
    144:'поражение леса верховым пожаром',
    145:'поражение леса низовым пожаром',
    105:'новое строительство зданий и сооружений (любых)',
    151:'новые земляные работы',
    152:'новое дорожное, линейное строительство',
    106:'новые свалки (любые)',
    107:'новое осушение (любое)',
    109:'новое затопление (любое)',
    200:'участки, непригодные для дешифрирования (любые)',
    201:'облака',
    202:'тень облаков',
    203:'дымка',
    2031:'прозрачная дымка',
    2032:'плотная дымка',
    2033:'радужная дымка (несведение каналов)',
}
objidval = 0

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

def FolderFiles(folder, miss_tmpt=None, type=None):
    dict_ = {}
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
                        dict_[name] = path
        elif miss_tmpt:
            if re.search(miss_tmpt, name):
                new_paths = FolderFiles(path, type=type)
                if new_paths is not None:
                    for new_name in new_paths:
                        dict_[r'%s/%s' % (name, new_name)] = new_paths[new_name]
    return dict_

class MaskSubtypeFolderIndex(dict):

    def __init__(self):
        self.corner = None
        self.subtype = None

    def FillFromDisk(self, corner, subtype):
        self.corner = corner
        self.subtype = subtype
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
                files = FolderFiles(datacatpath, miss_tmpt=None, type=datacats[datacat])
                # scroll(files)
                for name in files:
                    if not name in self[datacat]:
                        datapath = files[name]
                        self[datacat][name] = datapath
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

    def __init__(self, corner, datacat='img'):
        self.corner = corner
        self.bandclasses = {}
        self.subtypes = {}
        self.FillMaskBandclasses()
        self.FillMaskSubtypes(datacat=datacat)

    def FillMaskBandclasses(self):
        bandclasses = globals()['bandclasses']
        for bandclass in bandclasses:
            bandclasspath = r'%s/%s' % (self.corner, bandclass)
            if os.path.exists(bandclasspath):
                self.bandclasses[bandclass] = bandclasspath

    def FillMaskSubtypes(self, datacat='img'):
        datacats = globals()['datacats']
        subtypes = {'': None}
        for bandclass in self.bandclasses:
            bandclasspath = self.bandclasses[bandclass]
            datacatpath = r'%s/%s' % (bandclasspath, datacat)
            subtypedirs = FolderDirs(datacatpath, miss_tmpt='[#]')
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

    def Images(self, subtype='', bandclass='MS', datacat='img'):
        subtype_dict = self.Subtype(subtype)
        if subtype_dict:
            if bandclass in subtype_dict:
                if datacat in subtype_dict[bandclass]:
                    return subtype_dict[bandclass][datacat]
                else:
                    print('MS IMG FOLDER NOT FOUND: %s' % subtype)
            else:
                print('MS DATA NOT FOUND: %s' % subtype)

    def SaveBandsSeparated(self, subtype='', datacat='img'):
        full_imgs = self.Images(subtype, 'MS', datacat=datacat)
        if full_imgs:
            band_params = globals()['band_params']
            for ms_name in full_imgs:
                ms_path = full_imgs[ms_name]
                for channel in band_params:
                    band_num, bandclass = band_params[channel]
                    band_name = ms_name.replace('.tif', '_%s.tif' % channel)
                    band_path = r'%s\%s\%s\%s\%s' % (self.corner, bandclass, datacat, subtype, band_name)
                    band_folder = os.path.dirname(band_path)
                    suredir(band_folder)
                    SetImage(ms_path, band_path, band_num=1, band_reposition=[band_num], overwrite=False)
                print('BANDS WRITTEN: %s' % ms_name)
        else:
            print('FULL IMAGE DATA NOT FOUND: %s' % subtype)

    def GetKanPath(self, kan_name, subtype='', type=None, geom_path=None, use_source_pms=True):
        if type is None:
            type = GetKanTypeFromID(kan_name)
        kan_path = r'%s\%s\img\%s\%s' % (self.corner, type, subtype, kan_name)
        if os.path.exists(kan_path):
            print('FILE EXISTS: %s' % kan_path)
            return kan_path
        else:
            kan_folder, kan_id, tif = split3(kan_path)
            suredir(kan_folder)
            if type=='PMS' and (not use_source_pms):
                pass
            else:
                kan_id = DownloadKanopusFromS3(kan_id, kan_folder, type=type, geom_path=geom_path)
                if kan_id:
                    kan_path = fullpath(kan_folder, kan_id, tif)
            if os.path.exists(kan_path):
                print('FILE EXISTS: %s' % kan_path)
                return kan_path
            elif type=='PMS':
                ms_path = self.GetKanPath(kan_name.replace('.PMS','.MS'), subtype=subtype, type='MS', geom_path=geom_path)
                pan_path = self.GetKanPath(kan_name.replace('.PMS','.PAN'), subtype=subtype, type='PAN', geom_path=geom_path)
                if ms_path and pan_path:
                    pms_id = split3(pan_path)[1].replace('.PAN','.PMS')
                    pms_path = fullpath(kan_folder, pms_id, tif)
                    # scroll((pan_path, ms_path, pms_path))
                    pms_path = Pansharp(pan_path, ms_path, pms_path)
                    if pms_path:
                        return pms_path

    def GetVectorPath(self, name, dataclass, subtype='', type=None):
        if type is None:
            type = GetKanTypeFromID(name)
        vec_path_ = r'%s\%s\%s\%s\%s' % (self.corner, type, dataclass, subtype, name)
        vec_folder, vec_id, ext_ = split3(vec_path_)
        for ext in ['shp', 'json', 'geojson']:
            vec_path = fullpath(vec_folder, vec_id, ext)
            if os.path.exists(vec_path):
                return vec_path
        print('''VECTOR PATH NOT FOUND: %s with dataclass='%s' and subtype='%s' ''' % (name, dataclass, subtype))

    def ReprojectPanToMs(self, folder, subtype = ''):
        ms_imgs = self.Images(subtype, 'MS')
        if ms_imgs:
            for ms_name in ms_imgs:
                ms_path = ms_imgs[ms_name]
                geom_path = RasterCentralPoint(gdal.Open(ms_path), reference=None, vector_path=tempname('json'))
                pan_id = ms_name.replace('.MS', '.PAN')
                pan_path = self.GetKanPath(pan_id, subtype=subtype, type='PAN', geom_path=geom_path)
                delete(geom_path)
                if pan_path:
                    output_path = fullpath(folder, ms_name)
                    output_dir = os.path.dirname(output_path)
                    suredir(output_dir)
                    raster2raster([(pan_path, 1)], output_path, path2target=ms_path, method=gdal.GRA_CubicSpline,
                                  enforce_nodata=0, compress='DEFLATE', overwrite=False)

    def GetRasterMask(self, name, target, dataclass=['shp_auto', 'shp_hand'], colname='gridcode', subtype='',
                      bandclass=None, use_source_pms=True, quicksizes=None, train_folder=None, sat='kanopus',
                      img_target='IM4', colname_sec=None, replace=None, compress='DEFLATE', empty_default=0):
        if bandclass is None:
            bandclass = GetKanTypeFromID(name)
        targets = globals()['targets']
        if target in targets:
            target_id = targets[target]
        else:
            print('UNKNOWN TARGET: %s' % target)
            return None
        msk_path_ = r'%s\%s\%s\%s\%s' % (self.corner, bandclass, dataclass, subtype, name)
        msk_folder, msk_id_, ext_ = split3(msk_path_)
        neuro_id = Neuroid(msk_id_)
        if neuro_id:
            msk_id = '%s-%s' % (target_id, neuro_id)
            msk_path = fullpath(msk_folder, msk_id, 'tif')
            if os.path.exists(msk_path):
                return msk_path
            else:
                dataclass_list = obj2list(dataclass)
                img_path = self.GetKanPath(self, name, subtype=subtype, type=bandclass, geom_path=None,
                                           use_source_pms=use_source_pms)
                if img_path is None:
                    print('RASTER DATA NOT FOUND: %s' % name)
                    return None
                for dataclass in dataclass_list:
                    vec_path = self.GetVectorPath(name, dataclass, subtype='', type=None)
                    if vec_path:
                        break
                if vec_path is None:
                    print('VECTOR DATA NOT FOUND: %s' % name)
                    return None
                return self.CreateRasterMask(img_path, vec_path, msk_path, colname, quicksizes=quicksizes,
                                             train_folder=train_folder, sat=sat, img_target=img_target,
                                             colname_sec=colname_sec, replace=replace,
                                             compress=compress, empty_default=empty_default)
        else:
            print('CANNOT DEFINE NEUROID: %s' % name)
            return None

    def CreateRasterMask(self, img_path, vec_path, msk_path, colname, quicksizes=None, train_folder=None,
                         sat='kanopus', img_target='IM4', colname_sec=None, replace=None, compress='DEFLATE',
                         empty_default=0):
        msk_folder, msk_id, ext = split3(msk_path)
        target, neuro_id = Separate(msk_id, '-', num=1)
        suredir(msk_folder)
        msk_path, values = SetMask(img_path, vec_path, msk_path, colname, replace=replace, empty_default=empty_default,
            colname_sec=colname_sec, compress=compress, overwrite=False)
        report = {}
        if msk_path:
            report[''] = SetMaskReport(img_path, vec_path, msk_path, values)
            if train_folder:
                train_img_folder = r'%s\images\%s' % (train_folder, sat)
                suredir(train_img_folder)
                train_img_path = r'%s\%s-%s.tif' % (train_img_folder, img_target, neuro_id)
                copyfile(img_path, train_img_path)
                train_msk_folder = r'%s\images\%s\%s' % (train_folder, target, sat)
                suredir(train_msk_folder)
                train_msk_path = r'%s\%s-%s.tif' % (train_img_folder, target, neuro_id)
                copyfile(msk_path, train_msk_path)
            else:
                ql_img_path = None
            if quicksizes:
                for size_ in quicksizes:
                    size = StrSize(size_)
                    report[size] = OrderedDict()
                    ql_msk_path = r'%s\QL%s_m\%s__QL%s.tif' % (msk_folder, size, msk_id, size)
                    suredir(os.path.dirname(ql_msk_path))
                    if train_folder:
                        ql_img_folder = r'%s\quicklooks\%s\%s' % (train_folder, size, sat)
                        suredir(ql_img_folder)
                        ql_img_path = r'%s\%s-%s__QL%s.tif' % (ql_img_folder, img_target, neuro_id, size)
                    ql_msk_path, ql_values = SetQuicklook(img_path, vec_path, ql_msk_path, colname, ql_out=ql_img_path,
                                pixelsize=size, method=gdal.GRA_Average, replace=replace, empty_default=empty_default,
                                colname_sec=colname_sec, compress=compress, overwrite=False)
                    report[size] = SetMaskReport(img_path, vec_path, ql_msk_path, ql_values)
                    if ql_msk_path and ql_img_path:
                        ql_train_folder = r'%s\quicklooks\%s\%s\%s' % (train_folder, size, target, sat)
                        suredir(ql_train_folder)
                        ql_train_path = r'%s\%s-%s__QL%s.tif' % (ql_train_folder, target, neuro_id, size)
                        copyfile(ql_msk_path, ql_train_path)
        return msk_path, report

    def UpdateTrainData(self, target, bandclass='MS', subtype='', use_source_pms=True, dataclass=['shp_auto','shp_hand'],
                        colname='gridcode', quicksizes=None, train_folder=None, sat='kanopus', img_target='IM4',
                        colname_sec=None, replace=None, compress='DEFLATE', empty_default=0):
        imgs = self.Images(subtype, bandclass)
        reports = {}
        if imgs:
            for name in imgs:
                masking = self.GetRasterMask(self, name, target, dataclass=dataclass, colname=colname, subtype=subtype,
                 bandclass=bandclass, use_source_pms=use_source_pms, quicksizes=quicksizes, train_folder=train_folder,
                 sat=sat, img_target=img_target, colname_sec=colname_sec, replace=replace, compress=compress,
                 empty_default=empty_default)
                if isinstance(masking, tuple):
                    msk_path, msk_report = masking
                    for rep_id in msk_report:
                        if rep_id in reports:
                            reports[rep_id][name] = msk_report[rep_id]
                        else:
                            reports[rep_id] = {name: msk_report[rep_id]}
            final_datetime = str(datetime.now()).replace(' ', '_').replace(':', '-')
            report_name = 'report_%s.xls' % final_datetime
            for rep_id in reports:
                rep_id_path = r'%s\%s\mask\%s\%s' % (self.corner, bandclass, subtype, report_name)
                dict_to_xls(rep_id_path, reports[rep_id])
                SaveMaskValues(rep_id_path, reports[rep_id])

    def UpdateFromMS(self, bandclass='PAN', subtype='', use_source_pms=True):
        ms_imgs = self.Images(subtype, 'MS')
        if ms_imgs:
            errors = []
            for ms_name in ms_imgs:
                pan_name = ms_name.replace('.MS','.%s' % bandclass)
                geom_path = RasterCentralPoint(gdal.Open(ms_imgs[ms_name]), reference=None, vector_path=tempname('json'))
                kan_path = self.GetKanPath(pan_name, subtype=subtype, type=bandclass, geom_path=geom_path, use_source_pms=use_source_pms)
                delete(geom_path)
                if not kan_path:
                    errors.append(ms_name)
            if errors:
                scroll(errors, header='\nFAILED TO SAVE FILES:')

def GetKanTypeFromID(kan_id):
    if re.search('IM4-.+-.+', kan_id):
        if 'PMS' in kan_id.split('_')[4]:
            return 'PMS'
        else:
            return 'MS'
    else:
        if '.MS' in kan_id:
            return 'MS'
        elif '.PAN' in kan_id:
            return 'PAN'
        elif '.PMS' in kan_id:
            return 'PMS'

def KanCallSQL(kan_id, type=False):
    if re.search('IM4-.+-.+', kan_id):
        if type:
            date = kan_id.split('-')[2]
            kan_date = '%s-%s-%s' % (date[:4], date[4:6], date[6:])
            return '''"source='kanopus' and date(datetime)='%s' and type='%s'"''' % (kan_date, type.lower())
        else:
            print('KANOPUS TYPE NOT DEFINED, CANNOT DOWNLOAD DATA: %s' % kan_id)
    elif re.search(r'fr\d+_KV.+_3NP2_.+_P?S*\d*_.+', kan_id):
        # fr1_KV1_35000_27800_00_3NP2_08_S_005407_121118.tif
        # KV1_35000_27800_00_KANOPUS_20181112_075400_075527.SCN1.MS.L2.MD.xml
        fr, sat, loc1, loc2, loc3, np1, np2, type2, loc11, loc12 = kan_id.split('_')
        kan_part = '_'.join([sat, loc1, loc2])
        if not type:
            type = {'S': 'ms', 'PSS1': 'pan', 'PSS4': 'pms'}.get(type2)
        if type:
            # return '''"hashless_id like '%s' and source='kanopus' and type='%s'"''' % (type.lower(), kan_part)
            return '''"source='kanopus' and hashless_id LIKE '{}%'"'''.format(kan_part)
        else:
            print('KANOPUS TYPE NOT DEFINED, CANNOT DOWNLOAD DATA: %s' % kan_id)
    else:
        return '''"source='kanopus' and hashless_id='%s'"''' % kan_id

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

# Создать растровую маску на основе вектора
def SetMask(img_in, vec_in, msk_out, value_colname='gridcode', replace=None, empty_default=0,
            colname_sec=None, compress='DEFLATE', overwrite=False):
    if check_exist(msk_out, ignore=overwrite):
        return msk_out, GetValues(msk_out)
    if os.path.exists(vec_in):
        crs = get_srs(gdal.Open(img_in))
        vec_reprojected = tempname('shp')
        vec_to_crs(ogr.Open(vec_in), crs, vec_reprojected)
        if not os.path.exists(vec_reprojected):
            vec_reprojected = vec_in
        try:
            RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, value_colname=value_colname, value_colname_sec=colname_sec, compress=compress, overwrite=overwrite)
            values = GetValues(msk_out, replace=replace, band_num=1)
            return msk_out, values
        except:
            print('Rasterizing error: %s %s' % (img_in, vec_in))
            return None, None
    else:
        try:
            ds(msk_out, copypath=img_in, options={'bandnum': 1, 'dt': 1, 'compress': 'DEFLATE'}, overwrite=overwrite)
            default_replace = [None, {0: empty_default}][bool(empty_default)]
            values = GetValues(msk_out, replace=default_replace, band_num=1)
            return msk_out, values
        except:
            print('Rasterizing error: %s %s' % (img_in, vec_in))
            return None, None

# Создать загрублённые снимки и растровые маски на основе вектора
def SetQuicklook(img_in, vec_in, msk_out, colname, ql_out=None, pixelsize=None, method=gdal.GRA_Average,
                 replace=None, empty_default=0, colname_sec=None, compress='DEFLATE', overwrite=True):
    if ql_out is None:
        ql_out_ = tempname('tif')
    MakeQuicklook(img_in, ql_out_, epsg=None, pixelsize=pixelsize, method=method, overwrite=overwrite)
    msk_out, values = SetMask(ql_out_, vec_in, msk_out, colname, replace=replace, empty_default=empty_default,
                              colname_sec=colname_sec, compress=compress, overwrite=overwrite)
    if ql_out is None:
        delete(ql_out_)
    return msk_out, values

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

def DownloadKanopusFromS3(id, pout, type=None, geom_path = None):
    folder = tempname()
    command = r'''gu_db_query -w %s -d %s''' % (KanCallSQL(id, type), folder)
    if geom_path is not None:
        command += ' -v %s' % geom_path
    # print(command)
    os.system(command)
    kan_dirs = FolderDirs(folder)
    l = len(kan_dirs)
    if l == 1:
        for kan_long_id in kan_dirs:
            kan_id = '_'.join(kan_long_id.split('_')[:-1])+'.L2'
            kan_raster_path = folder_paths(kan_dirs[kan_long_id],1,'tif')[0]
            shutil.copyfile(kan_raster_path, fullpath(pout, kan_id, 'tif'))
            print('WRITTEN: %s' % kan_id)
    else:
        kan_id = None
        if l == 0:
            print('SCENE DATA NOT FOUND: %s' % id)
        else:
            print('MULTIPLE SCENES FOUND FOR: %s - %i scenes' % (id, l))
    destroydir(folder)
    return kan_id

def SetKanIdByType(kan_id, type):
    if kan_id is not None:
        types = ['PMS', 'PAN', 'MS']
        # print(kan_id, type)
        if not ('.%s' % type) in kan_id:
            for t in types:
                if t!=type:
                    kan_id = kan_id.replace('.%s' % type, '.%s' % t)
        return kan_id

def GetKanopusId(id, type='MS', geom_path=None, raster_dir=None):
    folder = tempname()
    raster_path = None
    band_id = ''
    for part in ['_red','_green','_blue','_nir']:
        if part in id:
            id = id.split(part)[0]
            band_id = part
            break
    if re.search(r'^KV.+SCN\d+.L2$', id):
        kan_id = id.replace('.L2', '.%s.L2' % type)
    elif re.search('^KV.+L2$', id):
        kan_id = id
    elif re.search('^KV.+.P?MS$', id) or re.search('^KV.+.PAN$', id):
        kan_id = id + '.L2'
    elif re.search('^KV.+SCN\d+$', id):
        kan_id = '%s.%s.L2' % (id, type)
    else:
        command = r'''gu_db_query -w %s -d %s''' % (KanCallSQL(id, type), folder)
        if geom_path is not None:
            command += ' -v %s' % geom_path
        print(command)
        os.system(command)
        kan_dirs = FolderDirs(folder)
        l = len(kan_dirs)
        if l == 1:
            for folder_name in kan_dirs:
                raster_path = folder_paths(folder,1,'tif')[0]
                kan_id = '_'.join(folder_name.split('_')[:-1])+'.L2'
        else:
            kan_id = None
            if l == 0:
                # if type!='MS':
                    # kan_id = GetKanopusId(id, type='MS', geom_path=geom_path)
                if kan_id is None:
                    # print('SCENE DATA NOT FOUND: %s' % id)
                    pass
            elif l > 1:
                print('MULTIPLE SCENES FOUND FOR: %s - %i scenes' % (id, l))
                files = folder_paths(folder,1,'tif')
                for file in files:
                    f,n,e = split3(file)
                    if id==n or Neuroid(n)==id:
                        folder_name = os.path.split(f)[1]
                        raster_path = file
                        kan_id = '_'.join(folder_name.split('_')[:-1]) + '.L2'
    kan_id = SetKanIdByType(kan_id, type)
    # print(raster_dir, kan_id)
    if (raster_dir is not None) and (kan_id is not None):
        if raster_path is None:
            command = r'''gu_db_query -w %s -d %s''' % (KanCallSQL(kan_id, type), folder)
            if geom_path is not None:
                command += ' -v %s' % geom_path
            os.system(command)
            kan_dirs = FolderDirs(folder)
            l = len(kan_dirs)
            if l == 1:
                raster_path = folder_paths(folder, 1, 'tif')[0]
        if raster_path is not None:
            copyfile(raster_path, fullpath(raster_dir, kan_id, 'tif'), overwrite=True)
    destroydir(folder)
    if kan_id is not None:
        kan_id += band_id
    return kan_id

def Pansharp(pan_path, ms_path, pms_path):
    command = r'python py2pci_pansharp.py %s %s %s -d TRUE' % (pan_path, ms_path, pms_path)
    command = command.replace('&','!!!!!!!')
    print(command)
    os.system(command)
    if os.path.exists(pms_path):
        print('PANSHARPENING SUCCESSFUL: %s' % split3(pms_path)[1])
        return pms_path
    else:
        print('PANSHARPENING ERROR: %s' % split3(pms_path)[1])

# Parse Kanopus name
def ParseKanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Resurs name
def ParseResurs(id):
    satid, loc1, sentnum, geoton, date, num1, ending = id.split('_')
    ending = ending.split('.')
    if len(ending) == 4:
        num2, scn, type, lvl = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, ''
    elif len(ending) == 5:
        num2, scn, type, lvl, grn = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn
    else:
        raise Exception('Wrong ending length for %s' % id)

# Parse Sentinel-2 name
def ParseSentinel2(id):
    # S2B_MSIL1C_20190828T043709_N0208_R033_T48VUP_20190828T082130
    # S2A_MSIL1C_20190828_T37VCD # shortid for time composits
    vals = id.split('_')
    if len(vals) == 7:
        satid, lvl, datetime, col, row, tile, datetime2 = id.split('_')
        cutid = ''
    elif len(vals) == 8:
        satid, lvl, datetime, col, row, tile, datetime2, cutid = id.split('_')
        tile += cutid
    elif len(vals) == 6:
        satid, lvl, datetime, col, row, tile = id.split('_')
    elif len(vals) == 4:
        satid, lvl, datetime, tile = id.split('_')
    else:
        return '', '', '', '', ''
    lvl = lvl[-3:]
    dt = datetime.split('T')
    if len(dt)==2:
        date, time = dt
    else:
        date = dt[0]
        time = ''
    return satid, date, time, tile, lvl

# Parse Sentinel-1 name
def ParseSentinel1(id):
    # S1B_IW_GRDH_1SDV_20190108T231417_20190108T231442_014409_01AD29_1DD8.SAFE
    vals = id.split('_')
    if len(vals) == 9:
        satid, mode, typeclass, lvl, datetime1, datetime2, orbit, ad, dd = vals
        lvl = mode+lvl+typeclass
    else:
        return '', '', '', '', ''
    dt = datetime1.upper().split('T')
    if len(dt)==2:
        date, time = dt
    else:
        date = dt[0]
        time = ''
    return satid, date, time, orbit, lvl

# Parse Landsat-8 name
def ParseLandsat8(id):
    vals = id.split('_')
    # LC08_L1TP_133019_20160830_20170321_01_T1
    if len(vals)==4:
        satid, lvl, date, loc = vals
    elif len(vals)==7:
        satid, lvl, loc, date, date2, lvl1, lvl2 = vals
    else:
        return '', '', '', ''
    if satid=='LC08':
        satid = 'LS8'
    if not (bool(re.search(r'\d{6}', loc)) and bool(re.search(r'\d{8}', date))):
        loc_ = date
        date = loc
        loc = loc_
    return satid, date, loc, lvl

# Получить neuroid из исходного имени файла (для 4-х канального RGBN)
def Neuroid(id):
    if re.search(r'^KV.+L2$', id):
        id = re.search(r'KV.+L2', id).group()
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = ParseKanopus(id)
        loc = loc1+loc2+scn[3:]
        if type == 'PMS':
            lvl += type
    # Ресурс-П обрабатывается только из гранул!
    elif re.search(r'^RP.+L2.GRN\d+$', id):
        id = re.search(r'RP.+L2.GRN\d+', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = ParseResurs(id)
        loc = loc1 + scn[3:] + grn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^S2[AB]', id):
        satid, date, time, loc, lvl = ParseSentinel2(id)
    elif re.search(r'^S1[AB]', id):
        satid, date, time, loc, lvl = ParseSentinel1(id)
    elif re.search(r'^LC08_', id):
        satid, date, loc, lvl = ParseLandsat8(id)
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = '%s-%s-%s-%s' % (satid, date, loc, lvl)
    return neuroid

def StrSize(size):
    strsize = str(size).strip(' 0')
    if strsize.endswith('.'):
        strsize = strsize[:-1]
    return strsize

# Получить значения маски. Заменить значения в конечном растре, в соответствии со словарём
def GetValues(file, replace=None, band_num=1):
    raster = gdal.Open(file, 1)
    if raster:
        band = raster.GetRasterBand(band_num)
        arr_ = band.ReadAsArray()
        if replace:
            for key in replace:
                if key in arr_:
                    arr_[arr_ == key] = replace[key]
            band.WriteArray(arr_)
        raster = None
        return ' '.join(list(np.unique(arr_)))
    else:
        print('Cannot open raster: %s' % file)

def SetMaskReport(img_in, vec_in, msk_out, values):
    report = OrderedDict()
    report['img_in'] = img_in
    report['vec_in'] = vec_in
    report['msk_out'] = msk_out
    report['values'] = values
    return report

def SaveMaskValues(val_path, report):
    values = []
    for name in report:
        name_vals = report.get('values')
        if name_vals:
            for val in flist(name_vals.split(' '), int):
                if not (val in values):
                    values.append(val)
    if values:
        values.sort()
        fin = OrderedDict()
        codes = globals()['codes']
        for val in values:
            fin[val] = codes.get(val, 'UNKNOWN')
        dict_to_csv(fullpath(val_path, 'mask_values.csv'), fin)