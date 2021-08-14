from geodata import *
from dotmap import DotMap

bandclasses = ('MS','PAN','PMS','BANDS','BANDS_nir','BANDSnir1','BANDSnir2')
datacats = {'img': ('tif'),
            'img_check': ('tif'),
            'mask': ('tif'),
            'shp_auto': ('shp','json','geojson'),
            'shp_hand': ('shp', 'json','geojson'),
            'test_result': ('shp','json','geojson'),
            }
satellite_types = {
    'Sentinel-2': {'tmpt': r'S2[AB]', 'folder': 'sentinel', 'base_tmpt': '^S2[A,B]', 'band_num': 4},
    'Sentinel-1': {'tmpt': r'S1[AB]', 'folder': 'sentinel-1', 'base_tmpt': '^S1[A,B]', 'band_num': 1, 'band_list': ['pan']},
    'Kanopus': {'tmpt': r'KV[1-6I]', 'folder': 'kanopus', 'base_tmpt': '^KV[1-6I]', 'band_num': 4},
    'Resurs': {'tmpt': r'RP\d.+_GEOTON_', 'folder': 'resurs', 'base_tmpt': '^RP\d', 'band_num': 4},
    'KSHMSA-VR': {'tmpt': r'RP\d.+_KSHMSA-VR_', 'folder': 'kshmsa_vr', 'base_tmpt': r'^RP\d.+_KSHMSA-VR_', 'band_num': 5, 'band_list': ['red', 'green', 'blue', 'nir1', 'nir2']},
    'KSHMSA-SR': {'tmpt': r'RP\d.+_KSHMSA-SR_', 'folder': 'kshmsa_sr', 'base_tmpt': r'^RP\d.+_KSHMSA-SR_', 'band_num': 5, 'band_list': ['red', 'green', 'blue', 'nir1', 'nir2']},
    'Meteor-KMSS50': {'tmpt': r'M\d.+_KMSS50', 'folder': 'meteor', 'base_tmpt': r'^M\d.+_KMSS50', 'band_num': 3, 'band_list': ['red','green','blue','tir1','tir2']},
    'Meteor-KMSS100': {'tmpt': r'M\d.+_KMSS100', 'folder': 'meteor', 'base_tmpt': r'^M\d.+_KMSS100', 'band_num': 3, 'band_list': ['1green','2nir','3red']},
    'Planet': {'tmpt': r'PLN.+', 'folder': 'planet', 'base_tmpt': 'Analytic', 'band_num': 4},
    'Landsat': {'tmpt': r'LS\d', 'folder': 'landsat', 'base_tmpt': '^LS\d', 'band_num': 4},
    # 'DigitalGlobe': {'tmpt': r'[DW]?[GV]?', 'folder': 'dg', 'base_tmpt': r'[DW]?[GV]?', 'band_num': 4},
} # By default, , 'band_list' = ['red', 'green', 'blue', 'nir']
band_params = {
    'pan': [1, 'PAN'],
    'red': [1, 'BANDS'],
    'green': [2, 'BANDS'],
    'blue': [3, 'BANDS'],
    'nir': [4, 'BANDS_nir'],
    'nir1': [4, 'BANDSnir1'],
    'nir2': [5, 'BANDSnir2'],
    'nirr': [1, 'BANDS'],
    'rred': [2, 'BANDS'],
    'swir1': [3, 'BANDS'],
    'swir2': [4, 'BANDS'],
    'tir1': [5, 'BANDS'],
    'tir2': [6, 'BANDS'],
    '1green': [1, 'BANDS'],
    '2nir': [2, 'BANDS'],
    '3red': [3, 'BANDS'],
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
mask_types = {
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
    'snow': {'id': 'SNW', 'folder': 'snow'},
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
    82: 'лишайниковые пустоши и тундры',
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

options = DotMap()
options['vin'] = None
options['imgid'] = 'IM4'
options['pms'] = False
options['quicksizes'] = None
options['empty'] = False
options['original'] = True
options['image_col'] = None
options['code_col'] = 'gridcode'
options['code_col_sec'] = None
options['compress'] = 'DEFLATE'
options['overwrite'] = True
options['replace'] = None
options['band_reposition'] = None
options['mulltiply_band'] = None
options['dg_metadata'] = None
options['xls'] = None
options['burn_value'] = None
options['pathmark'] = None
options['missmark'] = None
options['maskid'] = 'full'

class FolderDirs(dict):

    def __init__(self, folder, miss_tmpt=None):
        if os.path.exists(folder):
            for name in os.listdir(folder):
                path = fullpath(folder, name)
                if os.path.isdir(path):
                    if FindAny(path, miss_tmpt, default=False):
                        continue
                    self[name] = path

def FolderFiles(folder, miss_tmpt=None, type=None, full_name=True):
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
                        if full_name:
                            dict_[r'%s/%s' % (name, new_name)] = new_paths[new_name]
                        elif new_name in dict_:
                            print('FILE NAME DUPLICATE: %s' % new_name)
                        else:
                            dict_[os.path.basename(new_name)] = new_paths[new_name]
    return dict_

def Files(folder, extension=None):
    dict_ = {}
    for file in folder_paths(folder,1,extension=extension):
        dict_[Name(file)] = file
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

    def __init__(self, corner, datacats='img'):
        self.corner = corner
        self.bandclasses = {}
        self.subtypes = {}
        self.FillMaskBandclasses()
        self.FillMaskSubtypes(datacats=datacats)
        self.connected = {}
        self.qlreport = None
        self.qlreportids = {}
        self.qlpoints = [r'y:\\', r'\\172.21.195.160\thematic\S3_NATAROVA_']

    def FillMaskBandclasses(self, bandclass_list=[]):
        bandclasses = globals()['bandclasses']
        for bandclass in bandclasses:
            bandclasspath = r'%s/%s' % (self.corner, bandclass)
            if os.path.exists(bandclasspath):
                self.bandclasses[bandclass] = bandclasspath
            elif bandclass in bandclass_list:
                suredir(bandclasspath)
                self.bandclasses[bandclass] = bandclasspath
            else:
                # print('BANDCLASS NOT FOUND: %s' % bandclass)
                pass

    def FillMaskSubtypes(self, datacats='img'):
        if datacats is None:
            datacats = globals()['datacats']
        else:
            datacats = obj2list(datacats)
        self.subtypes[''] = {}
        for bandclass in self.bandclasses:
            self.subtypes[''][bandclass] = {}
            for datacat in datacats:
                bandclasspath = self.bandclasses[bandclass]
                datacatpath = r'%s/%s' % (bandclasspath, datacat)
                self.subtypes[''][bandclass][datacat] = datacatpath
                subtypedirs = FolderDirs(datacatpath, miss_tmpt=['#', 'set'])
                for subtype_dir in subtypedirs:
                    subtype = CorrectFolderName(subtype_dir, ['img', 'shp_hand', 'shp_auto', 'mask'])
                    if subtype in self.subtypes:
                        if bandclass in self.subtypes[subtype]:
                            self.subtypes[subtype][bandclass][datacat] = subtypedirs[subtype_dir]
                        else:
                            self.subtypes[subtype][bandclass] = {datacat: subtypedirs[subtype_dir]}
                    else:
                        self.subtypes[subtype] = {bandclass: {datacat: subtypedirs[subtype_dir]}}

    def Subtype(self, subtype):
        if subtype in self.subtypes:
            return self.subtypes[subtype]
        else:
            print('SUBTYPE NOT FOUND: %s' % subtype)

    def UpdateFolderTif(self, corner=None):
        if corner is None:
            self.connected = {}
        elif os.path.exists(corner):
            print('START CONNECTED')
            files = Files(corner, extension='tif')
            scroll(files, header='FILES:')
            self.connected.update(files)
        return self.connected

    def DataFolder(self, subtype='', bandclass='MS', datacat='img'):
        subtype_dict = self.Subtype(subtype)
        # print(subtype_dict)
        if subtype_dict:
            if bandclass in subtype_dict:
                # print(datacat, subtype_dict[bandclass])
                if datacat in subtype_dict[bandclass]:
                    return subtype_dict[bandclass][datacat]
                else:
                    print('MS IMG FOLDER NOT FOUND: "%s"' % subtype)
            else:
                print('MS DATA NOT FOUND: %s %s' % (subtype, bandclass))
        else:
            print('SUBTYPE DICT IS EMPTY: %s' % subtype)

    def Images(self, subtype='', bandclass='MS', datacat='img', miss_tmpt=None):
        image_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat=datacat)
        if image_folder:
            return FolderFiles(image_folder, miss_tmpt=miss_tmpt, type='tif')

    def SubtypeFolderName(self, subtype='', bandclass='MS', datacat='img'):
        if subtype:
            image_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat=datacat)
            if image_folder:
                return os.path.split(image_folder)[1]
            else:
                raise
        else:
            return ''

    def SaveBandsSeparated(self, subtype='', datacat='img', satellite='Kanopus'):
        full_imgs = self.Images(subtype, 'MS', datacat=datacat)
        subtype_folder_name = self.SubtypeFolderName(subtype=subtype, datacat=datacat)
        if full_imgs:
            band_list = globals()['satellite_types'].get(satellite, {}).get('band_list', ['red', 'green', 'blue', 'nir'])
            band_params = globals()['band_params']
            for ms_name in full_imgs:
                ms_path = full_imgs[ms_name]
                for channel in band_list:
                    band_num, bandclass = band_params[channel]
                    band_name = ms_name.replace('.tif', '_%s.tif' % channel)
                    band_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat=datacat)
                    if band_folder is None:
                        band_folder = self.UpdateSubtype(bandclass, subtype, datacat, subtype_folder_name=subtype_folder_name)
                    if band_folder is None:
                        print('BAND FOLDER NOT FOUND: %s %s %s' % (bandclass, subtype, datacat))
                    else:
                        suredir(band_folder)
                        band_path = fullpath(band_folder, band_name)
                        SetImage(ms_path, band_path, band_num=1, band_reposition=[band_num], overwrite=False)
                print('BANDS WRITTEN: %s' % ms_name)
        else:
            print('FULL IMAGE DATA NOT FOUND: %s' % subtype)

    def CreateQuicklookSubtype(self, ql_size, bandclass = 'MS', subtype='', datacat='img', satellite='Kanopus'):
        full_imgs = self.Images(subtype, bandclass, datacat=datacat)
        if full_imgs:
            full_folder_name = self.SubtypeFolderName(subtype=subtype, datacat=datacat)
            ql_appendix = '_%sm' % str(float(ql_size)).rstrip('0').rstrip('.')
            ql_folder_name = os.path.splitext(full_folder_name)[0] + ql_appendix
            ql_folder = self.UpdateSubtype(bandclass, subtype, datacat, subtype_folder_name=ql_folder_name)
            for full_name in full_imgs:
                full_path = full_imgs[full_name]
                ql_path = fullpath(ql_folder, Name(full_path) + ql_appendix, 'tif')
                MakeQuicklook(full_path, ql_path, pixelsize=ql_size, overwrite=False)
                print('WRITTEN: %s' % full_name)

    def VectorizeRasterMasks(self, bandclass='MS', subtype='', datacat='shp_auto', replace=None, delete_vals=0):
        band_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat=datacat)
        if band_folder is None:
            subtype_folder_name = self.SubtypeFolderName(subtype=subtype, datacat=datacat)
            band_folder = self.UpdateSubtype(bandclass, subtype, datacat, subtype_folder_name=subtype_folder_name)
        if band_folder is None:
            print('CANNOT FIND BAND FOLDER: %s' % subtype)
            return 1
        full_imgs = self.Images(subtype, bandclass, datacat=datacat, miss_tmpt='archive')
        if full_imgs is not None:
            for name in full_imgs:
                msk_path = full_imgs[name]
                vec_path = fullpath(band_folder, name[:-4], 'shp')
                VectorizeRaster(msk_path, vec_path, index_id='gridcode', bandnum=1, overwrite=True)
                ReplaceAttrVals(vec_path, 'gridcode', replace, func=lambda x: (0, x)[x>0], delete_vals=delete_vals)
                print('VECTOR WRITTEN: %s' % name)
        else:
            print('MASK DATA NOT FOUND: %s' % subtype)

    def FileFromPath(self, path):
        for qlpoint in self.qlpoints:
            source_folder = fullpath(qlpoint, path.split('natarova')[-1])
            files = folder_paths(source_folder, 1, 'tif')
            if files:
                return files[0]

    def DownloadQL(self, kan_id, kan_folder, geom_path = None):
        if '_cut' in kan_id:
            return None
        if kan_id in self.qlreportids:
            qlids = self.qlreportids[kan_id]
            if qlids:
                kan_file = fullpath(kan_folder, kan_id, 'tif')
                if len(qlids)==1:
                    source_file = self.FileFromPath(self.qlreport.get(qlids[0],{}).get('Path'))
                    if source_file:
                        copyfile(source_file, kan_file)
                        return kan_file
                else:
                    for qlid in qlids:
                        source_file = self.FileFromPath(self.qlreport.get(qlid, {}).get('Path'))
                        if source_file:
                            if IntersectRaster(source_file, geom_path):
                                copyfile(source_file, kan_file)
                                return kan_file
        else:
            print(kan_id)
            sys.exit()

    def GetKanPath(self, kan_name, subtype='', type=None, geom_path=None, use_source_pms=True, datacat='img'):
        if type is None:
            type = GetKanTypeFromID(kan_name)
        kan_folder = self.DataFolder(subtype=subtype, bandclass=type, datacat=datacat)
        # print('" "'.join(flist([subtype, kan_name, kan_folder], str)))
        if not kan_folder:
            sys.exit()
        kan_path = fullpath(kan_folder, kan_name)
        if os.path.exists(kan_path):
            print('FILE EXISTS: %s' % kan_path)
            return kan_path
        else:
            kan_folder, kan_id, tif = split3(kan_path)
            kan_id = kan_id.replace('.MD','')
            suredir(kan_folder)
            if self.qlreportids:
                fin_path = self.DownloadQL(kan_id, kan_folder, geom_path=geom_path)
                if fin_path:
                    print('DOWNLOADED QL: %s' % kan_id)
                    return fin_path
            if kan_id in self.connected:
                if IntersectRaster(self.connected[kan_id], geom_path):
                    copyfile(self.connected[kan_id], kan_path)
                    print('EXTRACT FROM CONNECTED: %s' % kan_id)
                    return kan_path
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
                ms_path = self.GetKanPath(kan_name.replace('.PMS','.MS'), subtype=subtype, type='MS', geom_path=geom_path, datacat=datacat)
                pan_path = self.GetKanPath(kan_name.replace('.PMS','.PAN'), subtype=subtype, type='PAN', geom_path=geom_path, datacat=datacat)
                if ms_path and pan_path:
                    pms_id = split3(pan_path)[1].replace('.PAN','.PMS')
                    pms_path = fullpath(kan_folder, pms_id, tif)
                    # scroll((pan_path, ms_path, pms_path))
                    pms_path = Pansharp(pan_path, ms_path, pms_path)
                    if pms_path:
                        return pms_path

    def GetVectorPath(self, name, datacat='shp_hand', subtype='', type=None):
        if type is None:
            type = GetKanTypeFromID(name)
        vec_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat=datacat)
        vec_path_ = fullpath(vec_folder, name)
        vec_folder, vec_id, ext_ = split3(vec_path_)
        for ext in ['shp', 'json', 'geojson']:
            vec_path = fullpath(vec_folder, vec_id, ext)
            if os.path.exists(vec_path):
                return vec_path
        print('''VECTOR PATH NOT FOUND: %s with dataclass='%s' and subtype='%s' ''' % (name, datacat, subtype))

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
        msk_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat='mask')
        msk_path_ = fullpath(msk_folder, name)
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
                rep_id_folder = self.DataFolder(subtype=subtype, bandclass=bandclass, datacat='mask')
                rep_id_path = fullpath(rep_id_folder, report_name)
                dict_to_xls(rep_id_path, reports[rep_id])
                SaveMaskValues(rep_id_path, reports[rep_id])

    def UpdateFromMS(self, bandclass='PAN', subtype='', use_source_pms=True, datacat='img'):
        ms_imgs = self.Images(subtype=subtype, bandclass='MS', datacat=datacat)
        if ms_imgs:
            errors = []
            if subtype:
                subtype_folder_name = os.path.split(self.DataFolder(subtype=subtype, bandclass='MS', datacat=datacat))[1]
            else:
                subtype_folder_name = subtype
            pan_folder = self.UpdateSubtype(bandclass, subtype, datacat, subtype_folder_name=subtype_folder_name)
            if bandclass=='PMS': print(pan_folder)
            # sys.exit()
            for ms_name in ms_imgs:
                pan_name = ms_name.replace('.MS','.%s' % bandclass)
                if pan_folder:
                    geom_path = RasterCentralPoint(gdal.Open(ms_imgs[ms_name]), reference=None, vector_path=tempname('json'))
                    kan_path = self.GetKanPath(pan_name, subtype=subtype, type=bandclass, geom_path=geom_path, use_source_pms=use_source_pms, datacat=datacat)
                    delete(geom_path)
                else:
                    kan_path = False
                if not kan_path:
                    errors.append(ms_name)
            if errors:
                scroll(errors, header='\nFAILED TO SAVE FILES:')

    def UpdateSubtype(self, bandclass, subtype, datacat, subtype_folder_name = None):
        if not bandclass in self.bandclasses:
            print('BANDCLASS NOT FOUND: %s' % bandclass)
            return None
        if subtype_folder_name is None:
            subtype_folder_name = subtype
        subtype_folder_path = self.GetSubtypeFolderPath(bandclass, datacat, subtype_folder_name)
        if subtype in self.subtypes:
            if bandclass in self.subtypes[subtype]:
                self.subtypes[subtype][bandclass][datacat] = subtype_folder_path
            else:
                self.subtypes[subtype][bandclass] = {datacat: subtype_folder_path}
        else:
            self.subtypes[subtype] = {bandclass: {datacat: subtype_folder_path}}
        suredir(subtype_folder_path)
        return subtype_folder_path.rstrip('\\')

    def GetSubtypeFolderPath(self, bandclass, datacat, subtype_folder_name):
        return r'%s\%s\%s\%s' % (self.corner, bandclass, datacat, subtype_folder_name)

    def ImportQLReport(self, xls_path_list):
        self.qlreport = XLSDict(xls_path_list)
        if self.qlreport:
            self.qlreportids = {}
            for qlid in self.qlreport:
                id = '_'.join(qlid.split('_')[:-1]) + '.L2'
                if id in self.qlreportids:
                    self.qlreportids[id].append(qlid)
                else:
                    self.qlreportids[id] = [qlid]

class NeuroMasking(OrderedDict):

    def __init__(self, setname = 'mask'):
        self.setname = setname
        self.options = globals()['options']

    def UpdateInput(self, input):
        if input:
            for key in input:
                if key in self:
                    self[key].update(input[key])
                else:
                    self[key] = input[key]

    def InputFromReport(self, xls_path, sheetnum=0):
        self.UpdateInput(xls_to_dict(xls_path, sheetnum=sheetnum))

    def InputFromPairs(self, pin):
        o = self.options
        self.UpdateInput(get_pair_paths(pin, pms=o.pms, original=o.original, pathmark=o.pathmark, missmark=o.missmark, imgid=o.imgid, dg_path=o.dg_metadata))

    def InputFromVector(self, pin):
        print('INPUT FROM VECTOR FUNCTION IS UNFINISHED')
        return None
        o = self.options
        vecids = None
        if vecids_path is not None:
            if os.path.exists(vecids_path):
                with open(vecids_path) as vecids_data:
                    vecis = vecids_data.read().split('\n')
        raster_paths = get_raster_paths(pin)
        self.UpdateInput(get_pairs(raster_paths, vin, o.image_col, vecids=o.vecids, split_vector=o.split_vector, pms=o.pms, original=o.original, dg_path=o.dg_metadata))

    def SetOptions(self, options_dict):
        for key in options_dict:
            if key in self.options:
                self.options[key] = options_dict[key]
            else:
                print('UNKNOWN OPTION: %s' % str(key))

    def SetRazmetka(self, pout):
        msk_end_values = {}
        o = self.options
        for i, neuroid in enumerate(self):
            if (neuroid is None):
                print('  %i -- NEUROID ERROR: %s\n' % (i + 1, str(neuroid)))
            elif self[neuroid]['pairing'] == False:
                if o.empty_mask and os.path.exists(str(self[neuroid].get('r'))):
                    # print('  %i -- VECTOR NOT FOUND, CREATING EMPTY MASK: %s\n' % (i, str(neuroid)))
                    pass
                else:
                    print('  %i -- PAIRING ERROR: %s\n' % (i + 1, str(neuroid)))
                    continue
            paths = get_paths(pout, neuroid, o.maskid, o.imgid, o.quicksizes, original=o.original)
            if paths:
                img_out, msk_out, quickpaths = paths
                img_in = self[neuroid]['r']
                vec_in = self[neuroid].get('v', '')
                if '&full_cloud' in img_in:
                    empty_value = 201
                elif 'no_cloud' in img_in:
                    empty_value = 0
                else:
                    # print('UNKNOWN EMPTY VALUE: %s' % str(neuroid))
                    empty_value = None
                if (not vec_in) and (empty_value is None):
                    self[neuroid]['report'] = 'FAILURE'
                    print('  %i -- EMPTY VALUE ERROR: %s\n' % (i + 1, str(neuroid)))
                    continue
                img_out = set_image(img_in, img_out, overwrite=self.options.overwrite, band_reposition=self.options.band_reposition, multiply=self.options.multiply_band)
                self[neuroid]['img_out'] = img_out
                if vec_in:
                    vals_mask, attr_mask = GetAttrVals(vec_in, self.options.code_col, func=None)
                else:
                    attr_mask = None
                # !!! Add checking vals_mask
                msk_out = set_mask(img_in, vec_in, msk_out, code_col=attr_mask, code_col_sec=self.options.code_col_sec,
                                   empty_value=self.options.empty_value, burn_value=self.options.burn_value, overwrite=self.options.overwrite)
                self[neuroid]['msk_out'] = msk_out
                if self.options.quickpaths:
                    for size in self.options.quickpaths:
                        ql_img_out, ql_msk_out = self.options.quickpaths[size]
                        set_quicklook(img_out, vec_in, ql_img_out, ql_msk_out, code_col=attr_mask,
                                      code_col_sec=self.options.code_col_sec, pixelsize=size, method=gdal.GRA_Average,
                                      empty_value=self.options.empty_value, overwrite=self.options.overwrite)
                if not msk_out.startswith('ERROR'):
                    replace = self.options.replace_vals
                    if replace is not None:
                        try:
                            ReplaceValues(msk_out, replace)
                            self[neuroid]['report'] = 'SUCCESS'
                            if self.options.quickpaths:
                                for size in self.options.quickpaths:
                                    ReplaceValues(self.options.quickpaths[size][1], replace)
                        except:
                            print('Error replacing values: %s' % neuroid)
                            self[neuroid]['report'] = 'ERROR: Mask names not replaced'
                    else:
                        self[neuroid]['report'] = 'SUCCESS'
                    try:
                        vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))
                        # all_codes = check_type(vals)
                        # max_type = max(all_codes, key=lambda key: all_codes[key])
                        # if max_type != maskid:
                            # print("Warning: masktype %s mismatch maskid %s" % (max_type, maskid))
                        for val in vals:
                            if val and (not val in msk_end_values):
                                if val in codes:
                                    msk_end_values[val] = codes[val]
                                else:
                                    print('Unknown code: %i' % val)
                                    msk_end_values[val] = 'UNKNOWN'
                        msk_values = ' '.join(flist(vals, str))
                    except:
                        print('Cannot get mask values for: %s' % neuroid)
                        msk_values = ''
                    self[neuroid]['msk_values'] = msk_values
                    minimum, maximum = RasterMinMax(img_out)
                    self[neuroid]['min'] = minimum
                    self[neuroid]['max'] = maximum
                    print('  %i -- MASKED: %s with: %s ; data range: %s-%s \n' % (i + 1, neuroid, msk_values, int(minimum), int(maximum)))
                else:
                    print('  %i -- ERROR: %s\n' % (i + 1, neuroid))
            else:
                self[neuroid]['report'] = 'ERROR: Source paths not found'
                print('  %i -- ERROR: Source paths not found for %s\n' % (i + 1, neuroid))
        report_name = 'report_{}.xls'.format(datetime.now()).replace(' ', '_').replace(':', '-')
        report_path = fullpath(pout, report_name)
        dict_to_xls(report_path, self)
        scroll(msk_end_values, header='\nCODES USED:')
        dict_to_csv(fullpath(pout, 'mask_values.csv'), msk_end_values)
        print('\nFINISHED -- REPORT SAVED TO %s' % report_path)
        if quicksizes:
            for size in quicksizes:
                ql_report = qlReport(r'%s\quicklook\%s' % (pout, size2str(size)), self, size)

def CorrectFolderName(folder_out, types='img'):
    folder = folder_out
    types = obj2list(types)
    for type in types:
        if re.search('^%s_' % type, folder_out):
            folder = folder_out[len(type)+1:]
        elif re.search('^[&$#]%s_' % type, folder_out):
            folder = folder_out[0]+folder_out[len(type)+2:]
    return folder

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
    print(command)
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
                if t!=type and (t in kan_id):
                    kan_id = kan_id.replace('.%s' % t, '.%s' % type)
                    # print(kan_id)
        return kan_id

def GetKanopusId(id, type='MS', geom_path=None, raster_dir=None):
    id = id.replace('.MD','')
    folder = tempname()
    raster_path = None
    band_id = ''
    cut = ''
    for part in ['_red','_green','_blue','_nir']:
        if part in id:
            id = id.split(part)[0]
            band_id = part
            break
    if re.search('cut\d+$', id):
        id, cut = id.split('cut')
        id = id.rstrip('_')
        cut = '_cut' + cut
    if re.search(r'^KV.+SCN\d+.L2$', id) or re.search(r'^RP.+SCN\d+.L2$', id):
        kan_id = id.replace('.L2', '.%s.L2' % type)
    elif re.search('^KV.+L2$', id) or re.search('^RP.+L2$', id):
        kan_id = id
    elif re.search('^KV.+.P?MS$', id) or re.search('^KV.+.PAN$', id) or re.search('^RP.+.P?MS$', id) or re.search('^RP.+.PAN$', id):
        kan_id = id + '.L2'
    elif re.search('^KV.+SCN\d+$', id) or re.search('^RP.+SCN\d+$', id):
        kan_id = '%s.%s.L2' % (id, type)
    elif re.search('^KV.+RS$', id):
        kan_id = id
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
                if type=='PMS':
                    kan_id = GetKanopusId(id, type='PAN', geom_path=geom_path)
                    if kan_id is not None:
                        kan_id = kan_id.replace('.PAN', '.%s' % type)
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
        kan_id += cut
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

# Получить пути к исходным данным для масок для разделённых векторных файлов (shp, json, geojson) и растровых снимков (tif)
def get_pair_paths(pin, pms = False, original = False, pathmark = None, missmark = None, imgid = None, dg_path = None):
    export = OrderedDict()
    for folder in obj2list(pin):
        paths = folder_paths(folder, 1)
        for path in paths:
            if (not FindAny(path, pathmark)) or FindAny(path, missmark, False):
                continue
            f,n,e = split3(path)
            if not e in ['shp', 'json', 'geojson', 'tif']:
                continue
            id = neuroid_extended(n, original=original, imgid=imgid, dg_path=dg_path)
            if id is None:
                if e=='tif':
                    print(path)
                continue
            if pms_exit(id, pms):
                continue
            if e == 'tif':
                if id in export:
                    export[id]['r'] = path
                else:
                    export[id] = {'r': path}
            elif e in ('shp', 'json', 'geojson'):
                if id in export:
                    export[id]['v'] = path
                else:
                    export[id] = {'v': path}
    for id in export:
        if ('v' in export[id]) and ('r' in export[id]):
            export[id]['pairing'] = True
        else:
            export[id]['pairing'] = False
    return export

def get_raster_paths(raster_path):
    raster_path = obj2list(raster_path)
    pinstr = '\n'.join(pin)
    if os.path.exists(globals()['source_paths']):
        with open(globals()['source_paths']) as path_data:
            pin_, paths_ = path_data.read().split('\n\n')
            if pin_ == pinstr:
                return paths_.split('\n')
    export = []
    for folder in raster_path:
        export.extend(folder_paths(folder, 1, 'tif'))
    with open(globals()['source_paths'], 'w') as path_data:
        path_data.write('{}\n\n{}'.format(pinstr, '\n'.join(export)))
        print('Written source paths to: %s' % globals()['source_paths'])
    return export

# Получить пути к исходным данным для масок для цельных векторных файлов
def get_pairs(raster_paths, vin, img_colname, vecids=None, split_vector=True, pms=False, original=False, pathmark=None, dg_path=None):
    export = OrderedDict()
    if vecids is None:
        vecids = get_col_keys(vin, img_colname)
    raster_names = flist(raster_paths, lambda x: split3(x)[1])
    for vecid in vecids:
        id = filter_id(vecid, pms=pms)
        for i, rasterid in enumerate(raster_names):
            if id == rasterid:
                try:
                    if not FindAny(raster_paths[i], pathmark):
                        raise Exception
                    neuroid = neuroid_extended(n, original=original, dg_path=dg_path)
                    if split_vector:
                        export[neuroid] = {'r': raster_paths[i], 'v': filter_dataset_by_col(vin, img_colname, vecid)}
                    else:
                        export[neuroid] = {'r': raster_paths[i], 'v': vin}
                    export[neuroid]['pairing'] = True
                except:
                    if not ('neuroid' in locals()):
                        neuroid = vecid
                    if neuroid:
                        if neuroid in export:
                            export[neuroid]['pairing'] = False
                        else:
                            export[neuroid] = {'pairing': False}
                finally:
                    print('%s pairing %s' % (('ERROR', 'SUCCESS')[bool(neuroid)], vecid))
                    break
    return export

# Расширенная функция расчёта neuroid, учитывающая готовые neuroid и названия разновременных композитов
def neuroid_extended(id, original=False, imgid=None, dg_path=None):
    cutsearch = re.search('__cut\d+$', id)
    if imgid is None:
        imgid = 'IM4'
    if cutsearch is not None:
        cut = cutsearch.group()
        id = id.split('__cut')[0]
    else:
        # print('NoCut: %s' % id)
        cut = ''
    if re.search(r'^%s-.+-\d+-.+-.+$' % imgid, id) or re.search(r'^IM4-.+-\d+-.+-.+$', id):
        return '%s-%s%s' % (imgid, '-'.join(id.split('-')[1:]), cut)
    elif re.search(r'^S[12][AB]-\d+-.+-.+$', id):
        return '%s-%s%s' % (imgid, id, cut)
    elif re.search(r'IMCH\d+__.+__.+', id):
        parts = id.split('__')[1:3]
    elif len(id.split('__'))==2:
        parts = id.split('__')
    else:
        newid = get_neuroid(id, original=original, dg_path=dg_path)
        if newid is not None:
            return newid + cut
        else:
            print('WRONG ID: %s' % id)
            return None
    vals = [globals()['imgid']]
    # scroll(parts)
    for part_id in parts:
        part_neuroid = neuroid_extended(part_id, original=original, dg_path=dg_path)
        vals.append(part_neuroid[part_neuroid.index('-')+1:])
    return '__'.join(vals) + cut

# Получить neuroid из исходного имени файла (для 4-х канального RGBN)
def get_neuroid(id, original=False, dg_path=None):
    if original:
        return id
    if dg_path:
        dg_files = folder_paths(dg_path, 1, 'tif')
    else:
        dg_files = None
    if re.search(r'^KV.+L2$', id):
        id = re.search(r'KV.+L2', id).group()
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[3:]
        if type == 'PMS':
            lvl += type
    # Ресурс-П обрабатывается только из гранул!
    elif re.search(r'^RP.+L2.GRN\d+$', id):
        id = re.search(r'RP.+L2.GRN\d+', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = parse_resurs(id)
        loc = loc1 + scn[3:] + grn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^RP.+L2', id):
        id = re.search(r'^RP.+L2', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = parse_resurs(id)
        loc = loc1 + scn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^S2[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel(id)
    elif re.search(r'^S1[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel1(id)
    elif re.search(r'^LC08_', id):
        satid, date, loc, lvl = parse_landsat8(id)
    elif re.search(r'.+-S2AS.+_P\d+', id):
        dg_id = re.search(r'^.+P\d+', id).group()
        dg_metavals = GetMetaDG(dg_id, dg_files)
        if dg_metavals is None:
            return None
        else:
            satid, date, time, loc, lvl = dg_metavals
    else:
        print('Unknown imsys for: %s' % id)
        return None
    imgid = globals()['imgid']
    neuroid = imgid+'-%s-%s-%s-%s' % (satid, date, loc, lvl)
    # IM4 в начале -- условность, его можно будет изменить на этапе обработки изображения, если в нём больше 4 каналов
    return neuroid

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Resurs name
def parse_resurs(id):
    # RP1_28244_05_GEOTON_20180713_050017_050036.SCN3.MS.L2
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

# Parse Sentinel name
def parse_sentinel(id):
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
def parse_sentinel1(id):
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
def parse_landsat8(id):
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

def GetMetaDG(id, dg_files):
    if dg_files:
        names = flist(dg_files, lambda x: split3(x)[1])
        if id in names:
            file = dg_files[names.index(id)]
            dg_proc = process().input(os.path.dirname(file))
            # scroll(dg_proc.get_ids(), header=id)
            dg_scene = dg_proc.scenes[0]
            satid = dg_scene.meta.name('[sat]')
            date = dg_scene.meta.name('[date]')
            time = dg_scene.meta.name('[time]')
            loc = dg_scene.meta.name('[location]')
            lvl = dg_scene.meta.name('[lvl]')
            # print(satid, date, time, loc, lvl)
            return satid, date, time, loc, lvl
    else:
        return parse_dg(id)

# Parse DG name
def parse_dg(id):
    print(id)
    satid = 'DG'
    lvl = 'LVL'
    vals = id.split('_')
    months = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    if re.search(r'.+-S2AS-.+_\d+_P\d+', id):
        datetime, sulvl, loc1 = vals[0].split('-')
        loc = ''.join([loc1,vals[1],vals[2]])
    elif re.search(r'.+-S2AS_R\d+C\d+.*-.+_\d+_P\d+', id):
        datetime = vals[0].split('-')[0]
        newlocs = vals[1].split('-')
        loc4 = ''.join(newlocs[:-1])
        loc1 = newlocs[-1]
        loc = ''.join([loc1,vals[2],vals[3],loc4])
    date = '20%s%s%s' % (datetime[:2], months[datetime[2:5]], datetime[5:7])
    time = datetime[7:]
    return satid, date, time, loc, lvl

# Получить полные пути к растрам в разметке (автоматически создаётся нужная директория)
def get_paths(pout, id, maskid, imgid, quicksizes, original=True):
    satellite_types = globals()['satellite_types']
    fail = True
    if re.search(r'IMCH\d+__.+__.+', id) and re.search('^IMCH\d+$', imgid):
        composite_types = globals()['composite_types']
        nameparts = id.split('__')
        # scroll(nameparts)
        name1, name2 = nameparts[1:3]
        for compid in composite_types:
            sat1 = satellite_types[composite_types[compid]['sources'][0]]['tmpt']
            sat2 = satellite_types[composite_types[compid]['sources'][1]]['tmpt']
            if re.search(sat1, name1.split('-')[0]) and re.search(sat2, name2.split('-')[0]):
                sat_folder = composite_types[compid]['folder']
                nameparts[0] = imgid
                imgname = '__'.join(nameparts)
                fail = False
                break
        if fail:
            print('Unknown time composite for %s')
            return None
    elif re.search(r'^IM[0-9RGBNP]+-.+-\d+-.+-.+$', id) and re.search('^IM[0-9RGBNP]+$', imgid):
        for satid in satellite_types:
            if re.search(satellite_types[satid]['tmpt'], id.split('-')[1]):
                sat_folder = satellite_types[satid]['folder']
                nameparts = id.split('-')
                nameparts[0] = imgid
                imgname = '-'.join(nameparts)
                fail = False
        if fail:
            print('Unknown satellite for: %s' % id)
            return None
    else:
        for satid in satellite_types:
            if re.search(satellite_types[satid]['base_tmpt'], id):
                sat_folder = satellite_types[satid]['folder']
                imgname = id
                fail = False
        if fail:
            print('Wrong id format: %s' % id)
            return None
    img_folder = r'%s\images\%s' % (pout, sat_folder)
    msk_type = globals()['mask_types'].get(maskid)
    if msk_type:
        msk_folder = r'%s\masks\%s\%s' % (pout, msk_type['folder'], sat_folder)
    else:
        print('Unknown mask type: %s' % msk_type)
        return None
    for folder in (img_folder, msk_folder):
        suredir(folder)
    img_path = fullpath(img_folder, imgname, 'tif')
    if original:
        msk_name = imgname
    else:
        if len(imgid) == 3:
            msk_name = msk_type['id']+id[3:]
        else:
            msk_name = msk_type['id'] + id[4:]
    msk_path = fullpath(msk_folder, msk_name, 'tif')
    if quicksizes:
        quickpaths = OrderedDict()
        for size in quicksizes:
            strsize = size2str(size)
            ql_img_folder = r'%s\quicklook\%s\images\%s' % (pout, strsize, sat_folder)
            suredir(ql_img_folder)
            ql_img_path = r'%s\%s__QL%s.tif' % (ql_img_folder, imgname, strsize)
            ql_msk_folder = r'%s\quicklook\%s\masks\%s\%s' % (pout, strsize, msk_type['folder'], sat_folder)
            suredir(ql_msk_folder)
            ql_msk_path = r'%s\%s__QL%s.tif' % (ql_msk_folder, msk_name, strsize)
            quickpaths[size] = (ql_img_path, ql_msk_path)
    else:
        quickpaths = None
    return (img_path, msk_path, quickpaths)

# Записать изображение, проверяя корректность его формата
# Если overwrite==False, то изображения в корректном формате пропускаются
def set_image(img_in, img_out, overwrite = False, band_reposition = None, multiply = None):
    if os.path.exists(img_out):
        repair, counter = check_image(img_out, split3(img_out)[1])
        if not (repair or overwrite):
            return img_out
    if os.path.exists(img_in):
        repair, counter = check_image(img_in, split3(img_out)[1], multiply=multiply)
    else:
        print('Path not found: %s' % img_in)
        return 'ERROR: Source file not found'
    if repair:
        return repair_img(img_in, img_out, counter, band_order = band_reposition, multiply = multiply)
    else:
        shutil.copyfile(img_in, img_out)
        return img_out

# Check if the image needs repair
def check_image(img_in, neuro, multiply = None):
    raster = gdal.Open(img_in)
    realBandNum = raster.RasterCount
    metaBandNum = 0
    img_type = neuro.split('__')[0].split('-')[0]
    if re.search(r'^IM\d+$', img_type):
        metaBandNum = int(img_type[2:])
    elif re.search(r'IM[RGBNP]$', img_type):
        metaBandNum = 1
    elif re.search(r'IMCH\d+$', img_type):
        metaBandNum = int(img_type[4:])
    elif FindAny(neuro, ['.PAN','_red','_green','_blue','_nir']):
        metaBandNum = 1
    else:
        satellite_types = globals()['satellite_types']
        for satid in satellite_types:
            if re.search(satellite_types[satid]['base_tmpt'], neuro):
                metaBandNum = satellite_types[satid]['band_num']
    counter = min((metaBandNum, realBandNum))
    if multiply is not None:
        return True, counter
    if metaBandNum > realBandNum:
        print('Not enough bands for: %s - got %i, need %i' % (img_in, realBandNum, metaBandNum))
        raise Exception
    elif metaBandNum < realBandNum:
        print('Band count mismatch for: %s - got %i, need %i' % (img_in, realBandNum, metaBandNum))
        return True, counter
    counter = min((metaBandNum, realBandNum))
    for i in range(1, counter + 1):
        band = raster.GetRasterBand(i)
        if band.DataType != 3 or band.GetNoDataValue() != 0:
            return True, counter
    return False, counter

# Записать растр снимка в установленном формате
def repair_img(img_in, img_out, count, band_order=None, multiply = None):
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

# Создать растровую маску на основе вектора
def set_mask(img_in, vec_in, msk_out, code_col='gridcode', code_col_sec=None, overwrite=False, empty_value=0, burn_value=None):
    if check_exist(msk_out, ignore=overwrite):
        return msk_out
    if os.path.exists(vec_in):
        crs = get_srs(gdal.Open(img_in))
        vec_reprojected = tempname('shp')
        vec_to_crs(ogr.Open(vec_in), crs, vec_reprojected)
        if not os.path.exists(vec_reprojected):
            vec_reprojected = vec_in
        print(burn_value)
        try:
            if burn_value is None:
                RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, value_colname=code_col, value_colname_sec=code_col_sec, compress=compress, overwrite=overwrite)
            else:
                RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, burn_value=burn_value, compress=compress, overwrite=overwrite)
            return msk_out
        except:
            # RasterizeVector(vec_reprojected, img_out, msk_out, data_type=2, value_colname=code_col, value_colname_sec=code_col_sec, compress=compress, overwrite=overwrite)
            print('Rasterizing error: %s %s' % (img_in, vec_in))
            return 'ERROR: Rasterizing error'
    elif empty_value is None:
        print('Empty value is None: skipping')
        return 'ERROR: Rasterizing error'
    else:
        try:
            # ds(msk_out, copypath=img_in, options={'bandnum': 1, 'dt': 1, 'compress': 'DEFLATE'}, overwrite=overwrite)
            CreateDataMask(img_in, msk_out, value=empty_value, nodata=0, bandnum=1)
            return msk_out
        except:
            print('Rasterizing error: %s %s' % (img_in, vec_in))
            return 'ERROR: Rasterizing error'

# Создать загрублённые снимки и растровые маски на основе вектора
def set_quicklook(img_in, vec_in, ql_out, msk_out, code_col='gridcode', code_col_sec=None, pixelsize=None, method=gdal.GRA_Average, empty_value=0, burn_value=None, overwrite=True):
    MakeQuicklook(img_in, ql_out, epsg=None, pixelsize=pixelsize, method=method, overwrite=overwrite)
    set_mask(ql_out, vec_in, msk_out, code_col=code_col, code_col_sec=code_col_sec, empty_value=empty_value, burn_value=burn_value, overwrite=overwrite)

def qlReport(folder, input, size):
    ql_input = OrderedDict()
    strsize = size2str(size)
    codes = globals()['codes']
    msk_end_values = OrderedDict()
    for line in input:
        _dict = input[line]
        new_line = '%s__QL%s' % (line, strsize)
        new_dict = OrderedDict()
        new_dict['r'] = _dict.get('r')
        new_dict['v'] = _dict.get('v')
        new_dict['pairing'] = _dict.get('pairing')
        new_dict['img_out'] = img_out = QlPathStr(_dict.get('img_out'), strsize)
        new_dict['msk_out'] = msk_out = QlPathStr(_dict.get('msk_out'), strsize)
        if os.path.exists(str(msk_out)):
            vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))
            for val in vals:
                if val and (not val in msk_end_values):
                    if val in codes:
                        msk_end_values[val] = codes[val]
                    else:
                        print('Unknown code: %i' % val)
                        msk_end_values[val] = 'UNKNOWN'
            msk_values = ' '.join(flist(vals, str))
            new_dict['report'] = 'SUCCESS'
            new_dict['msk_values'] = msk_values
        else:
            new_dict['report'] = 'FAILURE'
            new_dict['msk_values'] = ''
        if os.path.exists(str(img_out)):
            minimum, maximum = RasterMinMax(img_out)
            input[neuroid]['min'] = minimum
            input[neuroid]['max'] = maximum
        ql_input[new_line] = new_dict
    dict_to_csv(fullpath(folder, 'mask_values.csv'), msk_end_values)
    report_name = 'report_{}.xls'.format(datetime.now()).replace(' ', '_').replace(':', '-')
    report_path = fullpath(folder, report_name)
    dict_to_xls(report_path, ql_input)

def QlPathStr(str0, ql_add):
    if str0 is None:
        return None
    else:
        for spliter in [r'\images', '\masks']:
            pathparts = str0.split(spliter)
            if len(pathparts)==2:
                pout, partpath = pathparts
                return '%s\quicklook\%s%s%s__QL%s.tif' % (pout, ql_add, spliter, partpath[:-4], ql_add)

# Checks if name must be excluded as pansharpened or not pansharpened
def pms_exit(id, pms = False):
    if re.search('KV.+SCN\d+.+', id):
        if id.endswith('PMS'):
            if not pms:
                return True
        else:
            if pms:
                return True
    return False

def SetQlXlsPathList(path = r'\\172.21.195.2\thematic\!SPRAVKA\S3\\'):
    xls_path_list = []
    for index in range(1, 90):
        xls_path = r'%s\%i\%i.xls' % (path, index, index)
        if os.path.exists(xls_path):
            xls_path_list.append(xls_path)
    return xls_path_list