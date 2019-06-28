"""
Modification of the ImageProcess class converting its objects (processes and scenes to work with GDAL objects in Python (Datasets, Bands, etc.))
"""
import os
try:
    from osgeo import gdal, ogr
except:
    import gdal
    import ogr
import math
import numpy as np
import re
import xml.etree.ElementTree as et
import datetime as dtime

ath_corr_method_list = ['None', 'DOS1']
image_system_ids = ['All', 'Landsat', 'Sentinel']
image_system_list = [['Landsat', 'Sentinel'], ['Landsat'], ['Sentinel']]
#image_id_list = []
work_method_list = ['Single', 'Bulk', 'By_List']

# OS functions to read and write data to file system

# Checks if filename ends with '.tif(f)'
def TIF(path):
    if path.lower().endswith('.tiff') or path.lower().endswith('.tif'):
        return path
    else:
        return (path + '.tif')

# Checks if the file name fits the image system
def corner_file_check(filename, template):
    if re.search(template, filename) is not None:
        return True
    else:
        return False

# Returns a list of two lists: 0) all folders in the 'path' directory, 1) all files in it
def fold_finder(path):
    dir_ = os.listdir(path)
    fold_ = []
    file_ = []
    for name in dir_:
        full = path + '\\' + name
        if os.path.isfile(full):
            file_.append(full)
        else:
            fold_.append(full)
    return [fold_, file_]

# Searches filenames according to template and returns a list of full paths to them
# Doesn't use os.walk to avoid using generators
def walk_find(path, template, id_max=10000):
    if os.path.exists(path) and os.path.isdir(path):
        path_list = [path]
        path_list = [path_list]
    id = 0
    export_ = []
    while id < len(path_list) < id_max:
        for id_fold in range(len(path_list[id])):
            fold_, file_ = fold_finder(path_list[id][id_fold])
            if fold_ != []:
                path_list.append(fold_)
            for file_n in file_:
                s = re.search(template, file_n)
                if s is not None:
                    export_.append(file_n)
        id += 1
    if len(path_list) > id_max:
        raise Exception('Number of folder exceeds maximum = {}'.format(id_max))
    return export_

# Checks if all parameters for a band raster process are available
# I'm planning to delete it later when a method for param collection will be functional
def par_undef(par_list, parname_list=None):

    # Makes a list of predefined length filled with specified values
    # Considering the function is not used anywhere except par_undef() which is soon to be deleted it's defined within it
    def list_fill(obj, length):
        obj_list = []
        for i in range(length):
            obj_list.append(obj)
        return obj_list

    if parname_list is not None:
        try:
            def_list = list_fill('Object unavailable', len(par_list))
            for i in range(len(par_list)):
                parname_list[i] = def_list[i] + ': ' + parname_list[i]
        except IndexError:
            print(('Parname ' + str(parname_list[i]) + ' not found in par_list'))
    else:
        parname_list = list_fill('Object unavailable', len(par_list))
    for i in range(len(par_list)):
        if par_list[i] is None:
            raise NameError(parname_list[i])

# Converts a list with just one value to a single value changing format if necessary
def sing2sing(obj, sing_to_sing=True, digit_to_float=True):
    try:
        obj = list(obj)
        for val_id in range(len(obj)):
            obj[val_id] = str(obj[val_id])
    except:
        raise TypeError('Incorrect data type: list of strings is needed')
    if sing_to_sing:
        if len(obj) == 1:
            obj = obj[0]
            if digit_to_float:
                try:
                    obj = float(obj)
                except:
                    pass
    return obj

# Reads Landsat MTL file and returns metadata as dictionary
def mtl(path):
    mtl = open(path).read()
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

# Reads Landsat MTL file and returns metadata as element tree
def meta_sentinel(path, mtd=False):
    if mtd:
        path = os.path.split(path)[0] + r'\GRANULE'
        folder_mtd = os.listdir(path)[0]
        path = path + '\\' + folder_mtd + r'\MTD_TL.xml'
    try:
        return et.parse(path)
    except:
        raise Exception(('Cannot open file: ' + path))

# Converts data from a root call to a list
def iter_list(root, call):
    iter_list = []
    for obj in root.iter(call):
        iter_list.append({obj.tag: {'attrib': obj.attrib, 'text': obj.text}})
    return iter_list

# Processes the iter_list created by iter_list() to return list of values of a proper kind
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

# Filters the values from iter_return() by the attributes
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

# Returns dict values as a list
def mdval(dict_):
    return list(dict_.values())[0]

# Checks nodata value and format and if latter cannot contain negative values changes negative nodata to zero
def check_nodata(dtype, nodata):
    if (dtype in [bool, int, np.uint8, np.uint16, np.uint32] and nodata < 0) or (nodata is None):
        return int(0)
    else:
        return nodata

# Converts all values in list into integers
def intlist(list_):
    for val in range(len(list_)):
        list_[val] = int(list_[val])
    return list_

# Functions for working with GDAL

# Reprojects raster band
def reproject_band(band, s_proj, s_trans, t_proj, t_trans, t_shape, method=gdal.GRA_Bilinear, dtype=gdal.GDT_Byte):
    y_size, x_size = band.shape
    driver = gdal.GetDriverByName('MEM')
    s_ds = driver.Create('', x_size, y_size, 1, dtype)
    #s_ds.AddBand(dtype)
    s_ds.GetRasterBand(1).WriteArray(band)
    s_ds.SetGeoTransform(s_trans)
    s_ds.SetProjection(s_proj)
    t_ds = driver.Create('', t_shape[1], t_shape[0], 0)
    t_ds.AddBand(dtype)
    t_ds.SetGeoTransform(t_trans)
    t_ds.SetProjection(t_proj)
    gdal.ReprojectImage(s_ds, t_ds, None, None, method)
    return t_ds.ReadAsArray()

def band2raster(s_raster, t_raster, s_band_num=1, t_band_num=1, method=gdal.GRA_NearestNeighbour, dtype=None):
    s_proj = s_raster.GetProjection()
    s_trans = s_raster.GetGeoTransform()
    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    if s_band_num > s_raster.RasterCount:
        s_band_num = s_raster.RasterCount
    if t_band_num > t_raster.RasterCount:
        t_band_num = t_raster.RasterCount
    if dtype is None:
        dtype = s_raster.GetRasterBand(s_band_num).DataType
    s_band_array = s_raster.GetRasterBand(s_band_num).ReadAsArray()
    # For some reason reprojection takes time even if the rasters' parameters are the same
    if (s_proj == t_proj) and (s_trans == t_trans):
        t_band_array = s_band_array
    else:
        t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, dtype, method)
        #t_raster.AddBand(dtype)
    #t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, dtype, method)
    t_raster.GetRasterBand(t_band_num).WriteArray(t_band_array)
    return t_raster

# Creates gdal virtual dataset for use within scene class
def create_virtual_dataset(proj, geotrans, shape_, num_bands, dtype):
    y_res, x_res = shape_
    ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, num_bands, dtype)
    ds.SetGeoTransform(geotrans)
    ds.SetProjection(proj)
    return ds

# Calculation functions
# Most of them are better to be performed on C, C++, etc. to accelerate the procedures

# Calculates radiance for Landsat
def simple_radiance_landsat(band_array, param):
    RadMult, RadAdd = param
    band_array = np.copy(band_array) * RadMult
    return band_array + RadAdd

# Calculates radiance for Sentinel
def radiance_sentinel(band_array, param):
    rad_sun, sun_dist, quant = param
    coef = (rad_sun * sun_dist) / quant
    return band_array * coef

# Calculates reflectance for Landsat
def simple_reflectance(band_array, param):
    RefMult, RefAdd = param
    band_array = np.copy(band_array) * RefMult
    band_array = band_array + RefAdd
    band_array[band_array < 0.00] = 0.00
    return band_array

# Calculates reflectance for Sentinel
def reflectance_sentinel(band_array, quant=10000):
    return band_array / quant

# Returns DOS parameters from metadata
# Needs to be changed to process spatially referenced data
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

# Calculates dark radiance for Landsat (in DOS)
def rad_dark(band, param, noData=0, samp_size=1000):
    band_fil = np.copy(band)[band != noData]
    dark = band_fil.argsort()[:samp_size]
    DN = np.mean(band_fil[dark])
    return simple_radiance_landsat(DN, param)

# Calculates cosine of an object angle from metadata (can be applied to sattelites too)
def cos_sky(angle, not_zenith = True, not_radian = True):
    if not_radian:
        angle = math.radians(angle)
    if not_zenith:
        angle = (math.pi / 2) - angle
    return math.cos(angle)

# Calculates DN_dark from band_data
# Perhaps the results would be incorrect for deserted regions or winter scenes with no dark pixels
def dn_dark(band, mask=None, noData=0, samp_size=1000):
    band_fil = np.copy(band)
    if mask is not None:
        band_fil[mask] = noData
    band_fil = band_fil[band_fil != noData]
    dark = band_fil.argsort()[:samp_size]
    return np.mean(band_fil[dark])

# Calculates DOS reflectance for Landsat
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

# Calculates DOS reflectance for Sentinel
def dos_sentinel(band_array, param):
    quant, DN_dark = param
    subtr = (DN_dark / quant) - 0.01
    band_array = band_array / quant
    band_array = band_array - subtr
    band_array[band_array < 0.00] = 0.00
    return band_array

# Calculates NDVI
# With chinged input data may be used for calculation of any index with the same formula: NDWI, NDWI_Gao, etc.
def ndvi(red, nir):
    nom = nir - red
    denom = red + nir
    ndvi = np.zeros(red.shape, dtype=red.dtype)
    ndvi[denom!=0] = nom[denom!=0] / denom[denom!=0]
    return ndvi

# Objects of class "scene" represent single scenes of Landsat or Sentinel defined by a metadata file
# They contain paths to all the scene files as well as additional objects created from them
class scene(object):

    def __init__(self, path):
        self.path = path
        if self.path.endswith('_MTL.txt'):
            self.image_system = 'Landsat'
            self.mtl = mtl(path)
            file_names_dict = file_names(self.image_system, self.mtl)
            name = self.mtl['LANDSAT_PRODUCT_ID']
            self.descript = name[:5] + name[10:25]
            date_str = self.mtl['DATE_ACQUIRED']
        elif self.path.endswith('MTD_MSIL1C.xml'):
            self.image_system = 'Sentinel'
            self.msi = meta_sentinel(path)
            self.mtd = meta_sentinel(path, mtd=True)
            file_names_dict = file_names(self.image_system, self.msi)
            name = self.meta_call('PRODUCT_URI')
            self.descript = name[:19]
            date_str = self.meta_call('DATATAKE_SENSING_START')[:10]
        else:
            raise Exception('Unreckognized image system for path: {}'.format(path))
        year, month, day = intlist(date_str.split('-'))
        self.date = dtime.date(year, month, day)
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
                    #print('File not found: {}'.format(self.folder + '\\' + file_names_dict[key]))
                    pass
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
        return 'Object of class "scene" with:\n path: {p}\n image_system: {i_s}\n date: {d}\n {l} files are now available'.format(p=self.path, i_s=self.image_system, l=len(self), d=self.date)

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
            if file_id not in self.data_list:
                self.data_list.append(file_id)
            if 0 in dataset.ReadAsArray():
                self.mask(file_id)
            if (self.projection is None) or (self.transform is None):
                self.projection = dataset.GetProjection()
                self.transform = dataset.GetGeoTransform()
        else:
            print('Dataset already op'
                  'en: {}'.format(file_id))
        return self.data[file_id]

    # Closes Dataset
    def close(self, obj_id='1'):
        obj_id = str(obj_id)
        if obj_id in self.data_list:
            self.data.pop(obj_id)
            while obj_id in self.data_list:
                self.data_list.remove(obj_id)
        else:
            #print('No Dataset found: {}'.format(obj_id))
            pass
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
                self.mtl = mtl(self.input_path)
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
    def exist_check(self, data_id, add_str='', band_num=1):
        data_id = self.check_source_id(data_id)
        data_newid = data_id + add_str
        exist = data_newid in self.data_list
        if exist:
            return [False, data_newid, None]
        else:
            return [True, data_newid, self[data_id].GetRasterBand(band_num).ReadAsArray()]

    # Merges bands with different size if necessary
    def merge_band(self, target_data_id, source_dataset, data_newid = None, s_band_num=1, t_band_num=1, method = gdal.GRA_CubicSpline):
        if data_newid is None:
            data_newid = str(len(self) + 1)
        dtype = source_dataset.GetRasterBand(s_band_num).DataType
        if data_newid not in self.data_list:
            self.add_dataset(data_newid, copy=self[target_data_id], param={'num_bands': t_band_num, 'dtype': dtype})
        while t_band_num > self[data_newid].RasterCount:
            self[data_newid].AddBand(dtype)
        print('\nStart merging band by method {}'.format(method))
        data_new = band2raster(source_dataset, self[data_newid], s_band_num, t_band_num, method=method, dtype=dtype)
        print('Merging finished\n')
        self.data[data_newid] = data_new
        return self[data_newid]

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

    # Creates a new Dataset containing data from a band_array
    def array_to_dataset(self, data_newid, band_array, copy=None, param=None):
        if band_array.ndim == 2:
            band_num = 1
            band_array = [band_array]
        elif band_array.ndim == 3:
            band_num = len(band_array)
        else:
            raise Exception('Incorrect band_array shape: {}'.format(band_array.shape))
        if param is None:
            param = {'num_bands': 1}
        elif 'num_bands' not in param:
            param['num_bands'] = 1
        self.add_dataset(data_newid, copy, param)
        for band_id in range(1, band_num+1):
            self.data[data_newid].GetRasterBand(band_id).WriteArray(band_array[band_id-1])
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

    # Returns band of reflectance from source channel
    def reflectance(self, data_id, dataset=None, band_num=1):
        if dataset is not None:
            band_array = dataset.GetRasterBand(band_num).ReadAsArray()
            data_newid = '__test__'
            exist = True
        else:
            dataset = self[data_id]
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
            self.array_to_dataset(data_newid, band_array, copy=dataset, param={'dtype': 6})
        return self[data_newid]

    # Returns band of reflectance from source channel with DOS correction
    def dos(self, data_id, dos_id=1):
        dos_ = '_DOS' + str(dos_id)
        exist, data_newid, band_array = self.exist_check(data_id, dos_)
        if exist:
            t = None
            rayleigh = None
            print('Calculating {} reflectance from band {}'.format(dos_[1:], data_id))
            if self.image_system == 'Landsat':
                radiance_array = self.radiance(data_id).ReadAsArray()
                par = self.mtl_call(['SUN_ELEVATION', 'EARTH_SUN_DISTANCE', 'RADIANCE_MAXIMUM_BAND', 'REFLECTANCE_MAXIMUM_BAND', 'RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'], data_id)
                par_undef(par, ['SUN_ELEVATION', 'EARTH_SUN_DISTANCE', 'RADIANCE_MAXIMUM_BAND', 'REFLECTANCE_MAXIMUM_BAND', 'RADIANCE_MULT_BAND', 'RADIANCE_ADD_BAND'])
                radiance_dark = rad_dark(band_array, param=par[4:6])
                cos_sun = cos_sky(par[0])
                cos_sat = 1  # Not sure about proper source of it
                param = par[:4] + [cos_sun, cos_sat, t, rayleigh, radiance_dark]
                band_array = dos_reflectance(radiance_array, param, dos_id)
            elif self.image_system == 'Sentinel':
                quant = self.meta_call('QUANTIFICATION_VALUE')
                par_undef([quant], ['QUANTIFICATION_VALUE'])
                DN_dark = dn_dark(band_array)
                band_array = dos_sentinel(band_array, [quant, DN_dark])
            else:
                raise Exception('Unreckognized image system: {}'.format(self.image_system))
            self.array_to_dataset(data_newid, band_array, copy=self[data_id], param={'dtype': 6})
        return self[data_newid]

    # Returns band of reflectance from source channel with a predefined ath_corr method
    def ath_corr(self, data_id, method, dataset=None, band_num=1):
        if method == 'None':
            return self.reflectance(data_id, dataset=dataset, band_num=band_num)
        elif method == 'DOS1':
            return self.dos(data_id, 1)
        elif method == 'DOS2':
            return self.dos(data_id, 2)
        else:
            print('Unknown method: {}'.format(method))
            return None

    # Returns band of NDVI with a predefined ath_corr method
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

    # Returns band of NDVI with a predefined ath_corr method
    def ndwi(self, method='None'):
        data_newid = 'NDWI_{}'.format(method)
        if data_newid in self.data_list:
            return self.data[data_newid]
        green = self.ath_corr('3', method).ReadAsArray()
        if self.image_system == 'Landsat':
            nir = self.ath_corr('5', method).ReadAsArray()
        elif self.image_system == 'Sentinel':
            nir = self.ath_corr('8', method).ReadAsArray()
        else:
            raise Exception('Unreckognized image system: {}'.format(self.image_system))
        print('Calculating NDWI with {}'.format(method))
        band_array = ndvi(green, nir)
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
    def mask_apply(self, band_array, mask_list, nodata=-9999):
        nodata = check_nodata(band_array.dtype, nodata)
        mask_array = np.zeros(band_array.shape).astype(bool)
        for mask_id in mask_list:
            if mask_id not in self.outmask.keys():
                #print('Mask not found: {}'.format(mask_id))
                continue
            else:
                mask_array_ = self.outmask[mask_id].astype(bool)
                if mask_array.shape != mask_array_.shape:
                    print('Array shapes does not match, cannot apply mask: {}'.format(mask_array_.shape))
                    continue
                else:
                    mask_array[mask_array_] = True
        if mask_array.shape != band_array.shape:
            raise Exception('Array shapes does not match, cannot apply mask: band_array - {}, mask_array - {}'.format(band_array.shape,  mask_array.shape))
        else:
            band_array[mask_array] = nodata
        return band_array

    # Saves virtual Dataset to raster file masking it if necessary
    def save(self, data_id, path, mask_list=None, nodata=-9999, format='GTiff'):
        data_id = self.check_data_id(data_id)
        #if os.path.exists(path):
            #raise FileExistError('File already exists: {}'.format(path))
        xsize = self[data_id].RasterXSize
        ysize = self[data_id].RasterYSize
        driver = gdal.GetDriverByName(format)
        band_num = self[data_id].RasterCount
        dt = self[data_id].GetRasterBand(1).DataType
        outData = driver.Create(path, xsize, ysize, band_num, dt)
        for id in range(1, band_num+1):
            band_array = self[data_id].GetRasterBand(id).ReadAsArray()
            print(band_array.dtype)
            nodata_ = self[data_id].GetRasterBand(id).GetNoDataValue()
            if nodata_ is None:
                nodata_ = check_nodata(band_array.dtype, nodata)
            print(nodata_)
            if mask_list is not None:
                band_array = self.mask_apply(band_array, mask_list, nodata_)
            outData.GetRasterBand(id).WriteArray(band_array)
            outData.GetRasterBand(id).SetNoDataValue(nodata_)
        outData.SetProjection(self[data_id].GetProjection())
        outData.SetGeoTransform(self[data_id].GetGeoTransform())
        outData = None
        print('File saved: {}'.format(os.path.abspath(path)))
        return None

    # Creates a new Dataset from a mask
    def mask_dataset(self, mask_id, maskdataset_id=None, copy=None):
        if maskdataset_id is None:
            maskdataset_id = mask_id
        if maskdataset_id in self.data_list:
            return self[maskdataset_id]
        if copy is None:
            copy = self['4']
        self.array_to_dataset(maskdataset_id, self.outmask[mask_id], copy=copy, param={'dtype': gdal.GDT_Byte})
        #s.save('cloudmask', r'C:\sadkov\test.tif')
        return self[maskdataset_id]

# Objects of class "process" are sets of Landsats or Sentinel scenes which are to be processed in the same way
# Each of them must contain an input_list of paths to Landsat or Sentinel metadata files which are used for getting access to their data
class process(object):

    def __init__(self, input_path='', output_path='', image_system = ['Landsat', 'Sentinel'], image_id = 'L8OLI', work_method = 'Single', ath_corr_method = 'None', return_bands = False, filter_clouds = False):
        self.input_path = input_path #
        self.output_path = output_path # must be dir
        self.image_system = image_system
        #self.image_id = image_id
        self.work_method = work_method
        self.ath_corr_method = ath_corr_method
        self.return_bands = return_bands
        self.filter_clouds = filter_clouds
        self.input_list = []
        self.scene = [] # contains scenes
        self.corner_file_list = {
            'Landsat': 'LC\d\d_.+_MTL\.txt',
            'Sentinel': 'MTD_MSIL1C\.xml',
        }
        self.procedures = {
            'ndvi': self.ndvi,
            'ndwi': self.ndwi,
        }

    def __repr__(self):
        return 'Object of class "process" with\n input_path: {i_p}\n image_system: {i_s}\n work method: {w_m}\n athmospheric correction method: {a_c_m}\n return bands: {r_b}\n filter clouds: {f_c}\n {n_sc} scenes are now available'.format(i_p=self.input_path, i_s=self.image_system, w_m=self.work_method, a_c_m=self.ath_corr_method, r_b=self.return_bands, f_c=self.filter_clouds, n_sc=len(self.input_list))

    def __str__(self):
        return '{i_s} process.py of {n_sc} scenes available.'.format(i_s=self.image_system, n_sc=len(self.input_list))

    # Returns number of paths in the input_list
    def __len__(self):
        return len(self.input_list)

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

    # Checks if a single path is available in the input_list. If the list is empty fills it with self.input()
    def __bool__(self):
        if self.input_list == []:
            self.input()
        for s_path in self.input_list:
            if os.path.exists(s_path):
                return True
        return False

    # Adds new path to self.input_list
    def __iadd__(self, other):
        other_ = str(other)
        if os.path.exists(other_):
            if os.path.isdir(other_):
                raise Exception('Path to scene must be file, not dir: {}'.format(other_))
            if other_ in self.input_list:
                print('Input in the list: {}'.format(other_))
            else:
                self.input_list.append(other_)
                self.scene.append(None)
        else:
            print('Path not found')
        return self

    # Removes a path from self.input_list by number(int) or path(str)
    def __isub__(self, other):
        if isinstance(other, int):
            self.scene.pop(other)
            self.input_list.pop(other)
        elif isinstance(other, str):
            other_ = str(other)
            if other_ in self.input_list:
                self.scene.pop(self.input_list.index(other_))
                self.input_list.remove(other_)
            else:
                print('Not found in the input list: {}'.format(other_))
        else:
            print('Unexpected argument: type(other) = {}'.format(type(other)))
        return self

    # Returns scene by index
    def __getitem__(self, item):
        item = self.check_scene_id(item)
        if item < 0:
            item = len(self) + item
        if self.scene[item] is None:
            self.open_scene(item)
        return self.scene[item]

    # Fills self.input_path list with paths to scenes
    def input(self, in_path=None, clear=False):
        if clear:
            self.clear()
        if in_path is None:
            in_path = self.input_path
        if '" "' in in_path:
            self.work_method = 'By_List'
        elif os.path.isdir(in_path):
            self.work_method = 'Bulk'
        if in_path == '':
            raise Exception('No input_path found')
        elif not os.path.exists(in_path):
            raise Exception('Cannot find the input path: {}'.format(in_path))
        if self.work_method == 'Single':
            self += in_path
        elif self.work_method == 'Bulk':
            for im_sys in self.image_system:
                to_input = walk_find(in_path, self.corner_file_list[im_sys])
                for path in to_input:
                    self += path
        elif self.work_method == 'By_List':
            input = re.strip(in_path)
            for i in range(len(input)):
                if (input[i].startswith('"') and input[i].endswith('"')):
                    input[i] = input[i][1:-1]
                self += input[i]
        return self

    # Removes all data uploaded to the process
    def clear(self):
        self.close_scenes()
        self.scene = []
        self.input_list = []

    # Checks validity of scene_id value to the process
    def check_scene_id(self, id):
        try:
            id = int(id)
        except:
            raise TypeError('Cannot convert scene_id to int: {}'.format(id))
        if abs(id) > len(self):
            raise IndexError('Scene index out of range: {}'.format(id))
        return id

    # Opens one scene
    def open_scene(self, scene_id=0):
        scene_id = self.check_scene_id(scene_id)
        if self.scene[scene_id] is None:
            self.scene[scene_id] = scene(self.input_list[scene_id])
            #print('Opened scene from: {}'.format(self.input_list[scene_id]))
        return self.scene[scene_id]

    # Closes one scene
    def close_scene(self, scene_id=0):
        scene_id = self.check_scene_id(scene_id)
        if self.scene[scene_id] is not None:
            self.scene[scene_id] = None
            #print('Closed scene from: {}'.format(self.input_list[scene_id]))
        return None

    # Opens many scenes
    def open_scenes(self, open_list=None, except_list=None):
        if open_list is None:
            open_list = list(range(len(self)))
        if except_list is None:
            except_list = []
        for key in range(len(self)):
            if key not in except_list:
                self.open_scene(key)
        return None

    # Closes many scenes
    def close_scenes(self, close_list=None, except_list=None):
        if close_list is None:
            close_list = list(range(len(self)))
        if except_list is None:
            except_list = []
        for key in range(len(self)):
            if key not in except_list:
                self.close_scene(key)
        return None

    # Calculates ndvi from a scene
    def ndvi(self, scene_id=0):
        s = self[scene_id]
        if s:
            s.ndvi(self.ath_corr_method)
            #os.chdir(self.output_path)
            data_ids = ['NDVI_{}'.format(self.ath_corr_method)]
            filenames = ['{}_NDVI_{}.tif'.format(s.descript, self.ath_corr_method)]
            mask_0 = []
            if self.filter_clouds:
                if s.image_system == 'Landsat':
                    s.mask('QUALITY', 2720, True, 'Cloud')
                elif s.image_system == 'Sentinel':
                   vector_path = s.meta_call('MASK_FILENAME', check={'type': 'MSK_CLOUDS'}, mtd=True)
                   vector_path = '{}\\{}'.format(s.folder, vector_path)
                   if os.path.exists(vector_path):
                       s.vector_mask(vector_path, 'Cloud', data_id='4')
                   else:
                       print('Vector mask not found: {}'.format(vector_path))
                mask_0.append('Cloud')
            bands = {'Landsat': ['4', '5'], 'Sentinel': ['4', '8']}[s.image_system]
            mask = [mask_0 + bands]
            if self.return_bands:
                if self.ath_corr_method == 'None':
                    add = 'Ref'
                else:
                    add = self.ath_corr_method
                for band in bands:
                    data_ids.append('{}_{}'.format(band, add))
                    filenames.append('{}_B{}_{}.tif'.format(s.descript, band, add))
                    mask.append(mask_0 + [band])
            os.chdir(self.output_path)
            for id in range(len(data_ids)):
                s.save(data_ids[id], filenames[id], mask[id])
        else:
            print('No data found in {}'.format(str(s)))
        return None

    # Calculates ndwi from a scene
    def ndwi(self, scene_id=0):
        s = self[scene_id]
        if s:
            s.ndwi(self.ath_corr_method)
            #os.chdir(self.output_path)
            data_ids = ['NDWI_{}'.format(self.ath_corr_method)]
            outfolder, outfile = os.path.split(self.output_path)
            if os.path.exists(self.output_path) and not os.path.isfile(self.output_path):
                outfolder = self.output_path
                outfile = ''
            else:
                outfolder, outfile = os.path.split(self.output_path)
                if not os.path.exists(outfolder):
                    print('Cannot find output path')
                    return None
            if outfile == '':
                filenames = ['{}_NDWI_{}.tif'.format(s.descript, self.ath_corr_method)]
            else:
                filenames = [outfile]
            mask_0 = []
            if self.filter_clouds:
                if s.image_system == 'Landsat':
                    s.mask('QUALITY', 2720, True, 'Cloud')
                elif s.image_system == 'Sentinel':
                   vector_path = s.meta_call('MASK_FILENAME', check={'type': 'MSK_CLOUDS'}, mtd=True)
                   vector_path = '{}\\{}'.format(s.folder, vector_path)
                   if os.path.exists(vector_path):
                       s.vector_mask(vector_path, 'Cloud', data_id='3')
                   else:
                       print('Vector mask not found: {}'.format(vector_path))
                mask_0.append('Cloud')
            bands = {'Landsat': ['3', '5'], 'Sentinel': ['3', '8']}[s.image_system]
            mask = [mask_0 + bands]
            if self.return_bands:
                if self.ath_corr_method == 'None':
                    add = 'Ref'
                else:
                    add = self.ath_corr_method
                for band in bands:
                    data_ids.append('{}_{}'.format(band, add))
                    filenames.append('{}_B{}_{}.tif'.format(s.descript, band, add))
                    mask.append(mask_0 + [band])
            os.chdir(outfolder)
            for id in range(len(data_ids)):
                s.save(data_ids[id], filenames[id], mask[id])
        else:
            print('No data found in {}'.format(str(s)))
        return None

    # Performs procedures from a list for all scenes
    def run(self, procedure_list, delete_scenes=True):
        if isinstance(procedure_list, str):
            procedure_list = [procedure_list]
        for procedure in procedure_list:
            if procedure not in self.procedures:
                raise Exception('No procedure found: {}'.format(procedure))
        if self.input_list == []:
            try:
                self.input()
            except:
                print('No input data found, cannot run process')
                return None
        for scene_id in range(len(self)):
            for procedure in procedure_list:
                self.procedures[procedure](scene_id)
            if delete_scenes:
                self.close_scene(scene_id)
