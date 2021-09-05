from geodata import *

meta_folder = r'\\172.21.195.2\thematic\Sadkov_SA\code\razmetka_params'

sattelites = xls_to_dict(fullpath(meta_folder, 'sattelites.xlsx'))
legend = xls_to_dict(fullpath(meta_folder, 'legend.xlsx'))

def CheckFolder(folder, create = False):
    if not os.path.exists(folder):
        if create:
            os.makedirs(folder)
        else:
            raise FileNotFoundError(folder)

def GetSattelite(id):
    for sat in sattelites:
        if re.search(sattelites.get('tmpt', '^$'), id):
            return sat

def CheckImage(img_in, bands):
    raster = gdal.Open(img_in)
    for i in bands:
        band = raster.GetRasterBand(i)
        if band.GetMinimum()<0 or band.GetMaximum>65535:
            raise RazmetkaError( 'Data values out of limits: ' + img_in)
        if (band.DataType!=3) or (band.GetNoDataValue()!=0):
            return True, band_num
    return False, band_num

# Записать растр снимка в установленном формате
# Если минимальное или максимальное значение данных имеют занимают от 1% всех данных, они принимаются за nodata
def RepairImage(img_in, img_out, bands):
    d = isinstance(bands, dict)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':2, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(bands, range(1, count+1)):
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
        if d:
            multiplicator = bands.get(bin)
            if multiplicator is not None:
                arr_ = arr_ * multiplicator
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out

def SetImage(img_in, img_out, bands, overwrite = False):
    if os.path.exists(img_out):
        repair, counter = CheckImage(img_out, range(1, len(bands)+1))
        if not (repair or overwrite):
            return img_out
    if os.path.exists(img_in):
        repair, counter = CheckImage(img_in, bands)
    else:
        raise FileNotFoundError(img_in)
    if repair:
        return RepairImage(img_in, img_out, counter, band_order = band_reposition, multiply = multiply)
    else:
        shutil.copyfile(img_in, img_out)
        return img_out

# Returns:  1) are both files correct and containing geometry?
#           2) do their CRS match?
#           3) do their extents intersect?
def RasterVectorMatch(raster_path, vector_path):
    ds_in, lyr_in = get_lyr_by_path(vector_path)
    r_srs, r_geom = RasterParams(raster_path)
    if (lyr_in and r_srs) and r_geom:
        v_srs = lyr_in.GetSpatialRef()
        if v_srs:
            crs_match = r_srs.GetAttrValue('AUTHORITY', 1) == v_srs.GetAttrValue('AUTHORITY', 1)
            if not crs_match:
                r_geom.TransformTo(v_srs)
            for feat in lyr_in:
                v_geom = feat.GetGeometryRef()
                if r_geom.Intersects(v_geom):
                    return True, crs_match, True
            return True, crs_match, False
    return False, False, False

# Создать растровую маску на основе вектора
def SetMask(img_in, msk_out, vec_in = None, burn = None, filter_nodata = True, overwrite = False):
    if check_exist(msk_out, ignore=overwrite):
        return msk_out
    if vec_in is not None:
        valid, crs_match, intersect = RasterVectorMatch(img_in, vec_in)
        if valid:
            if intersect:
                if crs_match:
                    vec_used = vec_in
                else:
                    vec_used = tempname('shp')
                    vec_to_crs(ogr.Open(vec_in), get_srs(gdal.Open(img_in)), vec_used)
                if burn is None:
                    RasterizeVector(vec_used, img_in, msk_out, data_type = 2, burn_value = burn, filter_nodata = filter_nodata, compress = 'DEFLATE', overwrite = overwrite)
                else:
                    RasterizeVector(vec_used, img_in, msk_out, data_type = 2, value_colname = 'gridcode', filter_nodata = filter_nodata, compress = 'DEFLATE', overwrite = overwrite)
                if not crs_match:
                    f,n,e = split3(vec_used)
                    for file in folder_paths(f, 1):
                        if Name(file) == n:
                            delete(file)
            else:
                raise RazmetkaError('Raster and vector layers do not intersect: '  + img_in + ' ' + vec_in)
        else:
            raise RazmetkaError('Source invalid: ' + img_in + ' ' + vec_in)
    else:
        # Filter nodata doesnt work here
        CreateDataMask(img_in, msk_out, value = burn, nodata = 0, bandnum = 1)
    return msk_out

class RazmetkaError(Exception):

    def __init__(self, *args, **kwargs):
        pass

class FileList(list):

    def __init__(self, list):
        self.names = []
        for file in self:
            self.names.append(Name(file))

    def PopName(self, file):
        name = Name(file)
        if name in self.names:
            export = self.pop(self.names.index(name))
            self.names.pop(name)
            return export

class DataFolder:

    def __init__(self, corner):
        if os.path.exists(corner):
            self.corner = corner
        else:
            raise FileNotFoundError(corner)

    def DataFolder(self, band = 'MS', type = 'img', category = '', ql = False, cut = False, create_folder = False):
        band_folder = r'%s\%s' % (self.corner, band)
        CheckFolder(band_folder, create_folder)
        data_folder = r'%s\%s' % (band_folder, type)
        CheckFolder(data_folder, create_folder)
        if category:
            data_folder = r'%s\%s_%s' % (data_folder, type, category)
            CheckFolder(data_folder, create_folder)
        if ql:
            data_folder = r'%s\&q%s' % (data_folder, ql)
            CheckFolder(data_folder, create_folder)
        if cut:
            data_folder = r'%s\&cut_%s' % (data_folder, type)
            CheckFolder(data_folder, create_folder)
        return data_folder

    def DataFiles(self, band = 'MS', type = 'img', category = '', ql = False, cut = False, ext = 'tif'):
        try:
            data_folder = self.DataFolder(band = band, type = type, category = category, ql = ql, cut = cut)
        except FileNotFoundError as e:
            print('FOLDER NOT FOUND: %s' % e)
            return None
        files = {}
        for file in os.listdir(data_folder):
            fname, fext = os.path.splitext(file)
            if fext == ext:
                files[fname] = fullpath(data_folder, file)
        return files

class Razmetka:

    def __init__(self, mask_type = 'full', band_type = 'MS', vec_type = 'shp_hand', quicklook_size = None, ):
        self.maskt = mask_type
        self.bandt = band_type
        self.vect = vec_type
        self.qsize = quicklook_size
        self.input = OrderedDict()
        self.sets = []
        self.errors = []

    def __setattr__(self, key, value):
        assert isinstance(value, SceneRazmetka)
        self.input[key] = value

    def AddScene(self, img_in, vec_in, bands, burn, filter_nodata):
        scene = SceneRazmetka(img_in, vec_in = vec_in, bands = bands, burn = burn, filter_nodata = filter_nodata)
        if scene:
            self[scene.id] = scene
            return True
        else:
            return False

    def EnterInput(self, corner, category, bands = None, use_empty = False, use_cut = False, burn = None, filter_nodata = True):
        data = DataFolder(corner)
        img_files = data.DataFiles(band=self.bandt, type='img', category=category, ql=self.qlsize, cut=use_cut, ext='tif')
        count = 0
        if use_empty:
            for img_file in img_files:
                try:
                    count += bool(self.AddScene(img_file, None, bands, burn, filter_nodata))
                except RazmetkaError as e:
                    self.errors.append(e)
        else:
            vec_files = data.DataFiles(band=self.bandt, type=self.vect, category=category, ql=self.qlsize, cut=use_cut, ext='shp')
            if vec_files:
                vec_files = FileList(vec_files)
            else:
                raise RazmetkaError('Vector data not found: ' + corner + ' ' + category)
            for img_file in img_files:
                try:
                    vec_file = vec_files.PopName(Name(img_file))
                    count += bool(self.AddScene(img_file, vec_file, bands, burn, filter_nodata))
                except RazmetkaError as e:
                    self.errors.append(e)
        if count:
            self.sets.append((corner, category, bands, use_empty, use_cut, burn, filter_nodata, count))
        return count

    def MakeRazmetka(self, output_folder, replace = None, overwrite = False):
        img_folder = output_folder + '\images'
        msk_folder = output_folder + '\masks\\' + self.maskt
        for id in self.input:
            try:
                scene = self.input[id]
                img = scene.SceneImage(img_folder, overwrite = overwrite)
                msk = scene.SceneMask(msk_folder, overwrite = overwrite)
            except RazmetkaError as e:
                self.errors.append(e)


class SceneRazmetka:

    def __init__(self, img_in, vec_in = None, bands = None, burn = None, filter_nodata = True):
        self.id = Name(img_in)
        if vec_in is None:
            if burn is None:
                raise RazmetkaError('Pairing error ' + self.id)
        elif not os.path.exists(vec_in):
            raise RazmetkaError('Vector error: ' + self.vec)
        if not os.path.exists(img_in):
            raise RazmetkaError('Image error: ' + self.img)
        self.sat = GetSattelite(self.id)
        self.img = img_in
        self.AppendBands(bands)
        self.burn = burn
        self.vec = vec_in
        self.filter_nodata = filter_nodata

    def AppendBands(self, bands):
        img = gdal.Open(self.img)
        img_bands = list(range(1, img.RasterCount + 1))
        if img:
            if bands is None:
                self.bands = img_bands
            elif isinstance(bands, [list, dict]):
                d = isinstance(bands, [dict])
                for key in bands:
                    if not int(key) in img_bands:
                        raise RazmetkaError('Bands error: ' + str(bands) + ' ' + self.img)
                    elif d:
                        try: float(bands[key])
                        except: raise RazmetkaError('Bands multiply error: ' + str(bands) + ' ' + self.img)
                self.bands = bands
        else:
            raise RazmetkaError('Image error: ' + self.img)

    def SceneImage(self, img_folder, overwrite = False):
        img_out = r'{}\{}\{}.tif'.format(img_folder, self.sat, self.id)
        suredir(img_out)
        return SetImage(self.img, img_out, self.bands, overwrite = overwrite)

    def SceneMask(self, msk_folder, overwrite = False):
        msk_out = r'{}\{}\{}.tif'.format(msk_folder, self.sat, self.id)
        suredir(msk_out)
        return SetMask(self.img, msk_out, vec_in = self.vec, burn = self.burn, filter_nodata = self.filter_nodata, overwrite = overwrite)