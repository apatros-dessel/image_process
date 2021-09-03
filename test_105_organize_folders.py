from geodata import *

object_indices = [
    'o', # original
    '&c\d+', # cut
    '&ca\d+', # cut mask
    '&q\d+',  # quicklook
    '#s', # substandard
    '#d', # original degree
]

bandnames = ['_red', '_green', '_blue', '_nir']

raster_size = {
    'RP': {'MS': 2.1, 'PAN': 0.7, 'PMS': 0.7},
}

class WrongNameError(RuntimeError):

    def __init__(self, *args, **kwargs):  # Wrong file name template
        pass

def ParseName(name):
    if re.search(r'^RP.+GEOTON', name):
        sat = 'RP'
        idsearch = re.search(r'^RP.+SCN\d+', name)
        if idsearch:
            id = idsearch.group()
            ending = name[len(id):].split('.')
            if len(ending)>=3:
                return sat, ending[1], ending[2], id
            elif len(ending)==2:
                return sat, ending[1], '', id
            else:
                return sat, '', '', id
        else:
            return sat,'','',name
    else:
        raise WrongNameError(name)

class SceneObject(OrderedDict):

    def __init__(self, path):
        f, name, e = split3(path)
        assert e in ['shp', 'tif']
        self.path = path
        self.folder = f
        self.name = name
        self['ext'] = e
        if name.endswith('_border'):
            assert e == 'shp'
            name = name[:-7]
            self['border'] = True
        cutsearch = re.search('_cut\d+',name)
        self['cutend'] = ''
        while cutsearch:
            cutend = cutsearch.group()
            name = name[:-1*len(cutend)]
            self['cutend'] += cutend
            cutsearch = re.search('_cut\d+', name)
        self['band'] = ''
        for band in globals()['bandnames']:
            if name.endswith(band):
                self['band'] = band
                name = name[:-1*len(band)]
        qlsearch = re.search('_\d+\.?\d*m$', name)
        if qlsearch:
            self['ql'] = qlsearch.group()

        else:
            self['ql'] = ''
        self['sat'], self['type'], self['level'], self['baseid'] = ParseName(name)
        self.CheckRasterParams()

    def CheckRasterParams(self):
        advice = []
        if self['ext'] == 'tif':
            if self['cutend']:
                border_path = r'%s/&cut_shp/%s_border.shp' % (self.folder, self.name)
                if not os.path.exists(border_path):
                    # print('CUT BORDER NOT FOUND: %s' % border_path)
                    advice.append('Make border')
            if os.path.exists(self.path):
                raster = gdal.Open(self.path)
                if raster:
                    if self.IndexRasterCount() != raster.RasterCount:
                        print('WRONG RASTER COUNT: %s %i' % (self.path, raster.RasterCount))
                        advice.append('Fix raster count')
                    if raster.GetSpatialRef().IsGeographic():
                        print('DEGREE DATA WHERE UTM ANTICIPATED: %s' % self.path)
                        advice.append('Convert to UTM')
                    else:
                        if 0.9 < abs( self.IndexRasterPixelSize() / raster.GetGeoTransform()[1] ) < 1.1:
                            pass
                        else:
                            print('WRONG RASTER PIXEL SIZE: %s' % self.path)
                            advice.append('Fix pixel size')
                else:
                    print('CANNOT OPEN RASTER: %s' % self.path)
            else:
                print('RASTER NOT FOUND: %s' % self.path)

    def IndexRasterCount(self):
        if self['band']:
            return 1
        elif self['type']=='PAN':
            return 1
        elif self['sat'] in ['RP']:
            return 4

    def IndexRasterPixelSize(self):
        if self['ql']:
            ql_str = self['ql']
            return float(re.search('\d+\.?\d*', ql_str).group())
        else:
            return globals()['raster_size'][self['sat']][self['type']]

def IndexCutMask(name):
    if name.lower().endswith('shp'):
        if '_cut' in name:
            id = name.split('_cut')[0]
            return id
        else:
            raise WrongNameError()

def IndexCutImg(name):
    if name.lower().endswith('tif'):
        if '_cut' in name:
            id = name.split('_cut')[0]
            return id
        else:
            raise WrongNameError()

def IndexQuicklook(name):
    if name.lower().endswith('tif'):
        search = re.search('_Q?L?\d+\.\d*m&\.tif^', name)
        if search:
            id = name[:-1*(len(search.group()))]
            return id
        else:
            raise WrongNameError()

def IndexOriginalDegree(name):
    if name.lower().endswith('tif'):
        if '_deg' in name:
            id = name.split('_deg')[0]
            return id
        else:
            raise WrongNameError()

folder_names = {
    '$&cut_shp^': ('&cut_shp', IndexCutMask),
    '$&cut_img^': 'c',
    '$&\d+m^': 'q',
    '$#substandard^': '#s',
    '$#original_deg^': '#d',
}

def IndexFolder(folder_name, folder_path):
    for tmpt in globals()['folder_names']:
        if re.search(tmpt, folder_name):
            func = globals()['folder_names'][tmpt](folder_path)
            ids = {}
            for name in os.listdir(folder_path):
                id = func(name)
                if id in ids:
                    ids[id].append(name)
                else:
                    ids[id]
            return ids

class FolderDirs(OrderedDict):

    def __init__(self, folder, miss_tmpt=None):
        if os.path.exists(folder):
            for name in os.listdir(folder):
                path = fullpath(folder, name)
                if os.path.isdir(path):
                    if FindAny(path, miss_tmpt, default=False):
                        continue
                    self[name] = path

def ScriptFolder(corner, extensions=None):
    folders = FolderDirs(corner)
    if folders:
        result = OrderedDict()
        for name in folders:
            result[name] = ScriptFolder(folders[name])
        return result
    else:
        return len(folder_paths(corner, 1, extensions))

# scroll(ScriptFolder(r'\\172.21.195.2\thematic\!razmetka\database'), empty=False)

class ImageFolder(OrderedDict):

    def __init__(self, img_folder):
        self.type = os.path.split(img_folder)
        self.subtypes = ''

class ImageSubtype(OrderedDict):

    def __init__(self, img_folder):
        self.corner = img_folder
        self.folder_names = globals()['folder_names']
        if not os.path.exists(img_folder):
            raise FileNotFoundError
        names = os.listdir(img_folder)
        names.reverse()
        for name in names:
            path = '%s/%s' % (img_folder, name)
            if os.path.isfolder(path):
                assert FolderDirs(path) is None
                IndexFolder(name, path)
            else:
                id, ext = os.path.splitext(name)
                if ext.lower() == 'tif':
                    self.NewID(id)


        self.subtype = os.path.split(img_folder)

    def NewID(self, id):
        if id in self:
            print('ID EXISTS: %s' % id)
        else:
            self[id] = {}

def XLSDict(xls_path_list):
    xls_dict = OrderedDict()
    for xls_path in xls_path_list:
        new = xls_to_dict(xls_path)
        if new:
            xls_dict.update(new)
    return xls_dict

def XLSDictIds(xls_dict):
    if xls_dict:
        ids = {}
        for qlid in xls_dict:
            id = '_'.join(qlid.split('_')[:-1]) + '.L2'
            if id in ids:
                ids[id].append(qlid)
            else:
                ids[id] = [qlid]
        return ids

def FileFromPath(path, point):
    source_folder = fullpath(point, path.split('natarova')[-1])
    files = folder_paths(source_folder, 1, 'tif')
    if files:
        return files[0]
    else:
        print('FILES NOT FOUND: %s' % files)

def DownloadQL(kan_id, kan_folder, ids, point, report, geom_path = None):
    if '_cut' in kan_id:
        return None
    if kan_id in ids:
        qlids = ids[kan_id]
        if qlids:
            kan_file = fullpath(kan_folder, kan_id, 'tif')
            if len(qlids)==1:
                source_file = FileFromPath(report.get(qlids[0],{}).get('Path'), point)
                if source_file:
                    copyfile(source_file, kan_file)
                    return kan_file
            elif geom_path:
                for qlid in qlids:
                    source_file = FileFromPath(report.get(qlid, {}).get('Path'), point)
                    if source_file:
                        if IntersectRaster(source_file, geom_path):
                            copyfile(source_file, kan_file)
                            return kan_file
            else:
                # scroll(qlids, header=kan_id)
                for qlid in qlids:
                    source_file = FileFromPath(report.get(qlid, {}).get('Path'), point)
                    kan_file =  fullpath(kan_folder, qlid[:-4], 'tif')
                    copyfile(source_file, kan_file)
        else:
            print('QLIDS IS EMPTY: %s' % kan_id)
    else:
        print(kan_id)

def FillFromCut(folder, appendix = '\\&cut_img'):
    cut_folder = folder + appendix
    if os.path.exists(cut_folder):
        for cut in folder_paths(cut_folder,1,'tif'):
            name = Name(cut).split('_cut')[0]
            geom_path = RasterCentralPoint(gdal.Open(cut), reference=None, vector_path=tempname('json'))
            file = fullpath(folder, name, 'tif')
            if os.path.exists(file):
                print('ALREADY EXISTS: %s' % name)
                pass
            else:
                fin = DownloadQL(name, folder, ids, point, report, geom_path=geom_path)
                if fin:
                    print('WRITTEN: %s' % name)
                else:
                    print('ERROR: %s' % name)
            delete(geom_path)

def SetQlXlsPathList(path = r'\\172.21.195.2\thematic\!SPRAVKA\S3\\'):
    xls_path_list = []
    for index in range(1, 90):
        xls_path = r'%s\%i\%i.xls' % (path, index, index)
        if os.path.exists(xls_path):
            xls_path_list.append(xls_path)
    return xls_path_list

# for file in folder_paths(r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\!Resurs_Geoton\MS\img',1,'tif'):
    # obj = SceneObject(file)
report = XLSDict(SetQlXlsPathList(path = r'\\172.21.195.2\thematic\!SPRAVKA\S3\\'))
ids = XLSDictIds(report)
point = r'y:\\'

folders = FolderDirs(r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\!Resurs_Geoton\MS\img')
for folder_name in folders:
    folder = folders[folder_name]
    FillFromCut(folder)
sys.exit()
with open(r'C:\Users\Admin\Desktop\Kanopus.txt') as txt:
    ids_list = txt.read().split('\n')
    for id in ids_list:
        id = id.replace('.MS', '.PAN')
        if os.path.exists(r'e:\rks\new\%s.tif' % id):
            continue
        else:
            DownloadQL(id, r'e:\rks\new', ids, point, report, geom_path=None)
