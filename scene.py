pyth# Describes class "scene"

from service import *

print('hohoho')

athmo_corr_methods_list = ['None', 'DOS1', 'DOS2']

def create_virtual_dataset(proj, geotrans, shape_, num_bands, dtype):
    y_res, x_res = shape_
    ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, num_bands, dtype)
    ds.SetGeoTransform(geotrans)
    ds.SetProjection(proj)
    return ds

''' landsat '''

# Reads MTL file and returns metadata as dictionary
def mtl(path):
    mtl = open(path).read()
    '''
    folder, file = split_path(path)
    os.chdir(folder)
    try:
        if file == '':
            for name in os.listdir(folder):
                search_mtl = re.search(r".+_MTL.txt", name)
                if search_mtl is not None:
                    mtl = open(search_mtl.group()).read()
                    break
        else:
            mtl = open(file).read()
    except:
        print('Unable to find MTL by path: ' + path)
        return None
    '''
    mtl_list = re.split('  ', mtl)
    for i in range(len(mtl_list)):
        mtl_list[i] = mtl_list[i].strip()
    while '' in mtl_list:
        mtl_list.remove('')
    dict = {}
    for i in range(len(mtl_list)):
        if re.search('.+ = .+', mtl_list[i]) is not None:
            key = re.search('.+ =', mtl_list[i]).group()[:-2]
            if key in ['GROUP', 'END_GROUP']:
                continue
            val = re.search('= .+', mtl_list[i]).group()[2:]
            try:
                val = float(val)
            except:
                if (val.startswith('"') and val.endswith('"')):
                    val = val[1:-1]
            dict[key] = val
    return dict

# Returns bands' filenames as a dictionary
def file_names(image_system, source):
    file_names_dict = {}
    if image_system == 'Landsat':
        try:
            for key in source: # source should be mtl_dict(made by "mtl" function)
                if key.startswith('FILE_NAME_BAND'):
                    file_names_dict[key[15:]] = source[key]
        except:
            print('Unable to read MTL dictionary')
    elif image_system == 'Sentinel':
        root = source.getroot() # source should be tree (made by "meta_sentinel" function)
        for obj in root.iter('IMAGE_FILE'):
            file_name = obj.text
            band_id = re.search(r'_.{3}\b', file_name).group()
            if band_id[-2:].isdigit():
                band_id = str(int(band_id[-2:]))
            else:
                band_id = band_id[-3:]
            file_names_dict[band_id] = (file_name + '.jp2')
    else:
        print('Unreckognised image_system: {}'.format(image_system))
    return file_names_dict

''' Sentinel '''

def radiance_sentinel(band_array, param):
    rad_sun, sun_dist, quant = param
    coef = (rad_sun * sun_dist) / quant
    return band_array * coef

def reflectance_sentinel(band_array, quant=10000):
    return band_array / quant

def meta_sentinel(path, mtd=False):
    if mtd:
        path = os.path.split(path)[0] + r'\GRANULE'
        folder_mtd = os.listdir(path)[0]
        path = path + '\\' + folder_mtd + r'\MTD_TL.xml'
    try:
        return et.parse(path)
    except:
        raise Exception(('Cannot open file: ' + path))

def sentinel_mask_id(aux_band_list=None, cloud_mask=False):
    band_newid = ('NODATA')
    if aux_band_list is not None:
        for aux_band in aux_band_list:
            band_newid = (band_newid + '+' + str(aux_band))
    if cloud_mask:
        band_newid = (band_newid + '+CLOUDS')
    return band_newid

def iter_list(root, call):
    iter_list = []
    for obj in root.iter(call):
        iter_list.append({obj.tag: {'attrib': obj.attrib, 'text': obj.text}})
    return iter_list

def mdval(dict_):
    return list(dict_.values())[0]

def iter_return(iter_list, data='text', attrib=None):
    if isinstance(data, int):
        data = ['text', 'tag', 'attrib'][data]
    return_list = []
    if data == 'attrib':
        if attrib is None:
            for monodict in iter_list:
                return_list.append(mdval(monodict)['attrib'])
        else:
            for monodict in iter_list:
                return_list.append(mdval(monodict)['attrib'][str(attrib)])
    elif data == 'text':
        for monodict in iter_list:
            return_list.append(mdval(monodict)['text'])
    elif data == 'tag':
        for monodict in iter_list:
            return_list.append(list(monodict.keys())[0])
    return return_list

def attrib_filter(iter, check):
    filter = np.ones(len(iter)).astype(np.bool)
    for key in check:
        val = str(check[key])
        filter_key = []
        for monodict in iter:
            if key in mdval(monodict)['attrib']:
                filter_key.append((mdval(monodict)['attrib'][key])==val)
            else:
                filter_key.append(False)
        if True not in filter_key:
            raise Warning(('No value for ' + key + ' ' + val + ', cannot apply filter'))
            continue
        if len(filter_key) != len(filter):
            raise Warning('Search filter len are not equal')
        filter[np.array(filter_key).astype(np.bool)==False] = False
    return filter

''' athmo_corr '''

def simple_radiance_landsat(band_array, param):
    RadMult, RadAdd = param
    band_array = np.copy(band_array) * RadMult
    return band_array + RadAdd

def simple_reflectance(band_array, param):
    RefMult, RefAdd = param
    band_array = np.copy(band_array) * RefMult
    band_array = band_array + RefAdd
    band_array[band_array < 0.00] = 0.00
    return band_array

def dos_par(dospar=1, cos_sun = None, cos_sat = None, t = None, rayleigh = None, rad_dark = None):
    parlist = [None, [1,1,0], [1,cos_sun,0], [None,None,rayleigh], [None,None,None]]
    if dospar not in range(1,5):
        raise Exception(("Unknown method: DOS" +  str(dospar)))
    else:
        if dospar >= 2:
            par_undef([cos_sun], ['cos_sun'])
        if (dospar >= 3):
            par_undef([cos_sat, t], ['cos_sat', 't'])
            if dospar == 3:
                par_undef([rayleigh], ['rayleigh'])
            parlist[dospar][0] = math.exp((-1 * t) / cos_sat)
            parlist[dospar][1] = math.exp((-1 * t) / cos_sun)
            if dospar == 4:
                par_undef([rad_dark], ['rad_dark'])
                parlist[4][2] = math.pi * rad_dark
    if None in parlist[dospar]:
        raise Exception(('Unknown error calculating DOS' + str(dospar) + ' parameters'))
    else:
        return parlist[dospar]

def dos_reflectance(band_array, param, dos_id=1):

    sun_elev, sun_dist, rad_max, ref_max, cos_sun, cos_sat, t, rayleigh, rad_dark = param
    pid2 = math.pi * sun_dist ** 2
    e_sun = pid2 * rad_max / ref_max
    tau_v, tau_z, e_sky = dos_par(dos_id, cos_sun, cos_sat, t, rayleigh, rad_dark)
    sun_rad = tau_v * (e_sun * cos_sun * tau_z + e_sky) / pid2
    rad_path = rad_dark - 0.01 * sun_rad
    band_array = band_array - rad_path
    band_array[band_array < 0.00] = 0.00
    band_array = band_array / sun_rad
    return band_array

def rad_dark(band, param, noData=0, samp_size=1000):
    band_fil = np.copy(band)[band != noData]
    dark = band_fil.argsort()[:samp_size]
    DN = np.mean(band_fil[dark])
    return simple_radiance_landsat(DN, param)

def cos_sky(angle, not_zenith = True, not_radian = True):
    if not_radian:
        angle = math.radians(angle)
    if not_zenith:
        angle = (math.pi / 2) - angle
    return math.cos(angle)

def dn_dark(band, mask=None, noData=0, samp_size=1000):
    band_fil = np.copy(band)
    if mask is not None:
        band_fil[mask] = noData
    band_fil = band_fil[band_fil != noData]
    dark = band_fil.argsort()[:samp_size]
    return np.mean(band_fil[dark])

def dos_sentinel(band_array, param):
    quant, DN_dark = param
    subtr = (DN_dark / quant) - 0.01
    band_array = band_array / quant
    band_array = band_array - subtr
    band_array[band_array < 0.00] = 0.00
    return band_array

# Returns call for MTL dictionary from the parameter name and band id
def band_call(call, band_id=None):
    if band_id is None:
        return call
    if call.endswith('_'):
        add = ''
    else:
        add = '_'
    return (call + add + str(band_id))

ath_corr_method_list = ['None', 'DOS1', 'DOS2']
image_system_list = ['Landsat', 'Sentinel']
#image_id_list = []
work_method_list = ['Single', 'Bulk', 'By_List']

class scene(object):

    def __init__(self, path):
        self.path = path
        print(self.path)
        if self.path.endswith('_MTL.txt'):
            self.image_system = 'Landsat'
            self.mtl = mtl(path)
            file_names_dict = file_names(self.image_system, self.mtl)
            name = self.mtl['LANDSAT_PRODUCT_ID']
            self.descript = name[:5] + name[10:25]
        elif self.path.endswith('MTD_MSIL1C.xml'):
            self.image_system = 'Sentinel'
            self.msi = meta_sentinel(path)
            self.mtd = meta_sentinel(path, mtd=True)
            file_names_dict = file_names(self.image_system, self.msi)
            name = self.meta_call('PRODUCT_URI')
            self.descript = name[:19]
        else:
            raise Exception('Unreckognized image system for path: {}'.format(path))
        self.folder = os.path.split(path)[0] # full path to corner dir
        self.file_names = {}
        for key in file_names_dict:
            if os.path.exists(self.folder + '\\' + file_names_dict[key]):
                self.file_names[key] = file_names_dict[key]
            else:
                name_ = file_names_dict[key].replace('_B', '_band')
                if os.path.exists(self.folder + '\\' + name_):
                    self.file_names[key] = name_
                else:
                    print('File not found: {}'.format(self.folder + '\\' + file_names_dict[key]))
        self.data = {}
        self.data_list = [None]
        self.outmask = {}
        try:
            os.chdir(self.folder)
            band_data = gdal.Open(self.file_names['4'])
            self.projection = band_data.GetProjection()
            self.transform = band_data.GetGeoTransform()
            self.array_shape = (band_data.RasterYSize, band_data.RasterXSize)
            del(band_data)
        except:
            print('Cannot read projection data for the scene on path: {}'.format(path))
            self.projection = None
            self.transform = None
            self.array_shape = None

    def __repr__(self):
        return 'Object of class "scene" with:\n path: {p}\n image_system: {i_s}\n {l} files are now available'.format(p=self.path, i_s=self.image_system, l=len(self))

    def __str__(self):
        return '{i_s} scene with {l} files available.'.format(i_s=self.image_system, l=len(self))

    # Returns number of available files
    def __len__(self):
        return len(self.file_names)

    def __lt__(self, other):
        return len(self) < len(other)

    def __le__(self, other):
        return len(self) <= len(other)

    def __eq__(self, other):
        return len(self) == len(other)

    def __ne__(self, other):
        return len(self) != len(other)

    def __gt__(self, other):
        return len(self) > len(other)

    def __ge__(self, other):
        return len(self) >= len(other)

    # Checks if a single file is available in self.file_names
    def __bool__(self):
        return len(self) != 0

    # Returns band by index opening it if necessary
    def __getitem__(self, item):
        item = self.check_data_id(item)
        if item not in self.data_list:
            self.open(item)
        return self.data[item]

    # Checks validity of data_id value to the scene
    def check_data_id(self, id):
        id = str(id)
        if id not in list(self.file_names.keys()) + self.data_list:
            raise IndexError('Index not found: {}'.format(id))
        return id

    # Checks if data_id was present in the
    def check_source_id(self, id):
        id = str(id)
        if id not in list(self.file_names.keys()):
            raise IndexError('No source band with id = {} available'.format(id))
        return id

    # Opens file as dataset
    def open(self, file_id):
        file_id = self.check_source_id(file_id)
        os.chdir(os.path.split(self.path)[0])
        if file_id not in self.data_list:
            if os.path.exists(self.file_names[file_id]):
                dataset = gdal.Open(self.file_names[file_id])
            else:
                raise FileNotFoundError(('File not found: ' + self.file_names[file_id]))
            self.data[file_id] = dataset
            self.data_list.append(file_id)
            if 0 in dataset.ReadAsArray():
                self.mask(file_id)
            if (self.projection is None) or (self.transform is None):
                self.projection = band_data.GetProjection()
                self.transform = band_data.GetGeoTransform()
        else:
            print('Dataset already open: {}'.format(file_id))
        return self.data[file_id]

    # Closes Dataset
    def close(self, obj_id='1'):
        obj_id = str(obj_id)
        if obj_id in self.data_list:
            self.data.pop(obj_id)
            self.data_list.remove(obj_id)
        else:
            print('No Dataset found: {}'.format(obj_id))
        return None

    # Closes all Datasets
    def close_all(self):
        self.data = {}
        self.data_list = [None]
        return None

    # Creates a new empty virtual Dataset in scene.data
    def add_dataset(self, data_id, copy=None, param=None):
        data_id = str(data_id)
        if data_id in (list(self.file_names.keys()) + self.data_list):
            raise Exception('The dataset already exists: {}'.format(data_id))
        if copy is not None:
            if type(copy) == gdal.Dataset:
                x_res = copy.RasterXSize
                y_res = copy.RasterYSize
                proj = copy.GetProjection()
                trans = copy.GetGeoTransform()
                if copy.RasterCount > 0:
                    dtype = copy.GetRasterBand(1).DataType
                    num_bands = copy.RasterCount
            else:
                raise TypeError('copy = {} must be of type gdal.Dataset'.format(copy))
        else:
            y_res, x_res = self.array_shape
            proj = self.projection
            trans = self.transform
            dtype = 1
            num_bands = 1
        if param is not None:
            y_res = param.get('y_res', y_res)
            x_res = param.get('x_res', x_res)
            proj = param.get('proj', proj)
            trans = param.get('trans', trans)
            dtype = param.get('dtype', dtype)
            num_bands = param.get('num_bands', num_bands)
        self.data[data_id] = create_virtual_dataset(proj, trans, (y_res, x_res), num_bands, dtype)
        self.data_list.append(data_id)
        return self.data[data_id]

    # Gets metadata from Landsat MTL
    def mtl_call(self, call_list, band_id=None):
        if self.image_system != 'Landsat':
            raise Exception('Image system must be "Landsat"')
        if band_id is not None:
            band_id = str(band_id)
        if self.mtl is None:
            try:
                self.mtl = mtl(path)
            except:
                raise Exception('MTL data unavailable')
        par_list = []
        for call in call_list:
            par = None
            try:
                par = self.mtl[call]
            except:
                call = (call + '_' + band_id)
                par = self.mtl[call]
            if par is None:
                raise KeyError(call + ' value not found')
            par_list.append(par)
        return par_list

    # Gets metadata from Sentinel
    def meta_call(self, call, check=None, data='text', attrib=None, sing_to_sing=True, digit_to_float=True, mtd=False):
        if self.image_system != 'Sentinel':
            raise Exception('Image system must be "Sentinel"')
        if (attrib is not None):
            data = 'attrib'
        if mtd:
            iter = iter_list(self.mtd.getroot(), call)
        else:
            iter = iter_list(self.msi.getroot(), call)
        result = iter_return(iter, data, attrib)
        if check is not None:
            filter = attrib_filter(iter, check)
            result = list(np.array(result)[filter])
        return sing2sing(result, sing_to_sing, digit_to_float)

    # Checks if data_id is in the data_list and returns band from the original dataset if not
    def exist_check(self, data_id, add_str=''):
        data_id = self.check_source_id(data_id)
        data_newid = data_id + add_str
        exist = data_newid in self.data_list
        if exist:
            return [False, data_newid, None]
        else:
            return [True, data_newid, self[data_id].ReadAsArray()]

    # Gets parameters specifically to each function - not finished yet
    def get_param(self, function):
        landsat_dict = {
            'radiance': ['RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'],
            'reflectance': ['REFLECTANCE_MULT_BAND', 'REFLECTANCE_ADD_BAND'],
            'dos': ['SUN_ELEVATION', 'EARTH_SUN_DISTANCE', 'RADIANCE_MAXIMUM_BAND', 'REFLECTANCE_MAXIMUM_BAND', 'RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'],
        }
        sentinel_dict = {
            'radiance': ['SOLAR_IRRADIANCE', 'U', 'QUANTIFICATION_VALUE'],
            'reflectance': ['QUANTIFICATION_VALUE'],
            'dos': ['QUANTIFICATION_VALUE'],
        }
        param_dict = {'Landsat': landsat_dict, 'Sentinel': sentinel_dict}
        func_dict = {'Landsat': self.mtl_call, 'Sentinel': self.meta_call}
        param = []
        for call in param_dict[self.image_system][function]:
            param_to_add = func_dict[self.image_system](call)
            if param_to_add is not None:
                param.append(param_to_add)
            else:
                print('Parameter not found: {} is None'.format(call))
        return param

    # Processes band arrays according to a set of functions - not finished yet
    def array_process(self, band_array, function, data_id):
        landsat_dict = {
            'radiance': simple_radiance_landsat,
            'reflectance': simple_reflectance,
            'dos': dos_reflectance,
        }
        sentinel_dict = {
            'radiance': simple_radiance_landsat,
            'reflectance': simple_reflectance,
            'dos': dos_reflectance,
        }
        func_dict = {'Landsat': landsat_dict, 'Sentinel': sentinel_dict}
        if function not in func_dict[self.image_system]:
            raise Exception('Unreckognized function: {}'.format(function))
        else:
            print('Calculating {} from band {}'.format(function, data_id))
        param = self.get_param(function)
        band_array = func_dict[self.image_system][function](data_id, param)
        return band_array

    def array_to_dataset(self, data_newid, band_array, copy=None, param=None):
        if band_array.ndim == 2:
            band_num = 1
        elif band_array.ndim == 3:
            band_num = len(band_array)
        else:
            raise Exception('Incorrect band_array shape: {}'.format(band_array.shape))
        if param is not None:
            param['num_bands'] = 1
        else:
            param = {'num_bands': 1}
        self.add_dataset(data_newid, copy, param)
        self.data[data_newid].GetRasterBand(1).WriteArray(band_array)
        self.data_list.append(data_newid)
        return self[data_newid]

    # Returns band of radiance from source channel
    def radiance(self, data_id):
        exist, data_newid, band_array = self.exist_check(data_id, '_Rad')
        if exist:
            print('Calculating radiance from band {}'.format(data_id))
            if self.image_system == 'Landsat':
                param = self.mtl_call(['RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'], data_id)
                par_undef([band_array] + param, ['band_array', 'RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'])
                band_array = simple_radiance_landsat(band_array, param)
            elif self.image_system == 'Sentinel':
                sun_rad = self.meta_call('SOLAR_IRRADIANCE', check={'bandId': data_id})
                sun_dist = self.meta_call('U')
                quant = self.meta_call('QUANTIFICATION_VALUE')
                param = [sun_rad, sun_dist, quant]
                par_undef(param, ['SOLAR_IRRADIANCE', 'U', 'QUANTIFICATION_VALUE'])
                band_array = radiance_sentinel(band_array, param)
            else:
                raise Exception('Unreckognized image system: {}'.format(self.image_system))
            self.array_to_dataset(data_newid, band_array, copy=self[data_id], param={'dtype': 6})
        return self[data_newid]

    def reflectance(self, data_id):
        exist, data_newid, band_array = self.exist_check(data_id, '_Ref')
        if exist:
            print('Calculating reflectance from band {}'.format(data_id))
            if self.image_system == 'Landsat':
                param = self.mtl_call(['REFLECTANCE_MULT_BAND', 'REFLECTANCE_ADD_BAND'], data_id)
                par_undef([band_array] + param, ['band_array', 'REFLECTANCE_MULT_BAND', 'REFLECTANCE_ADD_BAND'])
                band_array = simple_reflectance(band_array, param)
            elif self.image_system == 'Sentinel':
                quant = self.meta_call('QUANTIFICATION_VALUE')
                par_undef([quant], ['QUANTIFICATION_VALUE'])
                band_array = reflectance_sentinel(band_array, quant)
            else:
                raise Exception('Unreckognized image system: {}'.format(self.image_system))
            self.array_to_dataset(data_newid, band_array, copy=self[data_id], param={'dtype': 6})
        return self[data_newid]

    def dos(self, data_id, dos_id=1):
        dos_ = '_DOS' + str(dos_id)
        exist, data_newid, band_array = self.exist_check(data_id, dos_)
        if exist:
            t = None
            rayleigh = None
            print('Calculating {} reflectance from band {}'.format(dos_[1:], data_id))
            if self.image_system == 'Landsat':
                par = self.mtl_call(['SUN_ELEVATION', 'EARTH_SUN_DISTANCE', 'RADIANCE_MAXIMUM_BAND', 'REFLECTANCE_MAXIMUM_BAND', 'RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'], data_id)
                par_undef(par, ['SUN_ELEVATION', 'EARTH_SUN_DISTANCE', 'RADIANCE_MAXIMUM_BAND', 'REFLECTANCE_MAXIMUM_BAND', 'RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'])
                radiance_dark = rad_dark(band_array, param=par[4:6])
                cos_sun = cos_sky(par[0])
                cos_sat = 1  # Not sure about proper source of it
                param = par[:4] + [cos_sun, cos_sat, t, rayleigh, radiance_dark]
                band_array = dos_reflectance(band_array, param, dos_id)
            elif self.image_system == 'Sentinel':
                quant = self.meta_call('QUANTIFICATION_VALUE')
                par_undef([quant], ['QUANTIFICATION_VALUE'])
                DN_dark = dn_dark(band_array)
                band_array = dos_sentinel(band_array, [quant, DN_dark])
            else:
                raise Exception('Unreckognized image system: {}'.format(self.image_system))
            self.array_to_dataset(data_newid, band_array, copy=self[data_id], param={'dtype': 6})
        return self[data_newid]

    def ath_corr(self, data_id, method):
        if method == 'None':
            return self.reflectance(data_id)
        elif method == 'DOS1':
            return self.dos(data_id, 1)
        elif method == 'DOS2':
            return self.dos(data_id, 2)
        else:
            print('Unknown method: {}'.format(method))
            return None

    # Calculate NDVI
    def ndvi(self, method='None'):
        data_newid = 'NDVI_{}'.format(method)
        if data_newid in self.data_list:
            return self.data[data_newid]
        red = self.ath_corr('4', method).ReadAsArray()
        if self.image_system == 'Landsat':
            nir = self.ath_corr('5', method).ReadAsArray()
        elif self.image_system == 'Sentinel':
            nir = self.ath_corr('8', method).ReadAsArray()
        else:
            raise Exception('Unreckognized image system: {}'.format(self.image_system))
        print('Calculating NDVI with {}'.format(method))
        band_array = ndvi(red, nir)
        self.array_to_dataset(data_newid, band_array, copy=self['4'], param={'dtype': 6})
        return self[data_newid]

    # Creates mask from raster band
    def mask(self, data_id, nodata=0, include=False, mask_id=None):
        data_id =self.check_data_id(data_id)
        if mask_id is None:
            mask_id = data_id
        mask_array = np.full((self[data_id].RasterYSize, self[data_id].RasterXSize), include)
        mask_array[self[data_id].ReadAsArray()==nodata] = not include
        self.outmask[mask_id] = mask_array
        return self.outmask[mask_id]

    # Creates mask from vector layer
    def vector_mask(self, vector_path, mask_id, data_id=None):
        mask_ogr = ogr.Open(vector_path)
        if mask_ogr.GetLayerCount() == 0:
            return None
        layer = mask_ogr.GetLayer()
        if data_id is None:
            temp_ds = self.add_dataset('temp_ds')
        else:
            temp_ds = self.add_dataset('temp_ds', copy=self[data_id])
        temp_ds.AddBand(1)
        target_band = temp_ds.GetRasterBand(1)
        target_band.SetNoDataValue(0)
        try:
            s=gdal.RasterizeLayer(temp_ds, [1], layer, burn_values=[1])
        except:
            print(('No pixels to filter in vector mask: ' + vector_path))
        self.outmask[mask_id] = target_band.ReadAsArray().astype(np.bool)
        self.close('temp_ds')
        return self.outmask[mask_id]

    # Filters raster array with a set of masks
    def mask_apply(self, band_array, mask_list, nodata=0):
        for mask_id in mask_list:
            if mask_id not in self.outmask.keys():
                #print('Mask not found: {}'.format(mask_id))
                continue
            else:
                mask_array = self.outmask[mask_id]
            if mask_array.shape != band_array.shape:
                raise Exception('Array shapes does not match, cannot apply mask')
            else:
                band_array[mask_array==True] = nodata
        return band_array

    def save(self, data_id, path, mask_list=None, nodata=0, format='GTiff'):
        xsize = self[data_id].RasterXSize
        ysize = self[data_id].RasterYSize
        driver = gdal.GetDriverByName(format)
        band_num = self[data_id].RasterCount
        dt = self[data_id].GetRasterBand(1).DataType
        outData = driver.Create(path, xsize, ysize, band_num, dt)
        for id in range(1, band_num+1):
            band_array = self[data_id].GetRasterBand(id).ReadAsArray()
            if mask_list is not None:
                band_array = self.mask_apply(band_array, mask_list, nodata)
            outData.GetRasterBand(id).WriteArray(band_array)
            outData.GetRasterBand(id).SetNoDataValue(nodata)
        outData.SetProjection(self[data_id].GetProjection())
        outData.SetGeoTransform(self[data_id].GetGeoTransform())
        outData = None
        print('File successfully saved: {}'.format(os.path.abspath(path)))
        return None

    def mask_dataset(self, mask_id, maskdataset_id='None', copy=None):
        if maskdataset_id is None:
            maskdataset_id = mask_id
        self.array_to_dataset(maskdataset_id, self.outmask[mask_id], copy=s['4'])
        s.save('cloudmask', r'C:\sadkov\test.tif')
        return None

