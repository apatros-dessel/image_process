# Version 0.3

try:
    from osgeo import gdal, ogr, osr
except:
    import gdal
    import ogr
    import osr

from tools import *

import geodata

import landsat
import planet

# Constants


default_output = os.getcwd() # default output directory for a process

imsys_dict = {
    'LST': landsat,
    #'SNT': sentinel,
    'PLN': planet,
}


'''
-- keeping here until new modules will be made

# Set image systems available for analysis
image_system_list = [
    'LST',                  # LANDSAT
    'SNT',                  # SENTINEL
    'PLN',                  # PLANET
]

# Set spacecraft list
spacecraft_list = [
    'LS8',                  # LANDSAT-8
    'SN2',                  # SENTINEL-2A
    'S2B',                  # SENTINEL-2B
    'PLN',                  # PLANET
]

# Templates for searching metadata files
corner_file_list = {                                # Helps to find metadata files
            'Landsat-8':    r'L[CE]\d\d_.+_MTL\.txt',
            'Sentinel-2':   r'MTD_MSIL\d[CA]\.xml',
            'Planet':       r'\d+_\d+_\S+_Analytic\S*_metadata.xml',
        }


# Set indexes for different channels in different image systems 
# Landsat-8
band_dict_lsat8 = {
    'coastal': '1',
    'blue': '2',
    'green': '3',
    'red': '4',
    'nir': '5',
    'swir1': '6',
    'swir2': '7',
    'pan': '8',
    'cirrus': '9',
    'tirs1': '10',
    'tirs2': '11'
}
# Sentinel-2
band_dict_s2 = {
    'coastal_aerosol': '1',
    'blue': '2',
    'green': '3',
    'red': '4',
    'vegetation red edge 1': '5',
    'vegetation red edge 2': '6',
    'vegetation red edge 3': '7',
    'nir': '8',
    'narrow nir': '8b',
    'water vapour': '9',
    'swir - cirrus': '10',
    'swir1': '11',
    'swir2': '12'
}
'''

# Set default types of composites
composites_dict = {
    'RGB':      ['red', 'green', 'blue'],           # Natural colours
    'NIR':      ['nir', 'red', 'green'],            # False colours
    'UFC':      ['swir2', 'swir1', 'red'],          # Urban False Colour
    'AGR':      ['swir1', 'nir', 'blue'],           # Agriculture
    'GEOL':     ['swir2', 'red', 'blue'],           # Geology
    'BAT':      ['red', 'green', 'coastal'],        # Bathymetric
    'APN':      ['swir2', 'swir1', 'narrow nir'],   # Athmospheric penetration
    'SWIR':     ['swir2', 'narow nir', 'red'],
    'SWIR-2':   ['blue', 'swir1', 'swir2'],
}

# Set default types of indices
index_dict = {
    'NDVI': ('Normalized',  ['nir', 'red'],     6),
    'NDWI': ('Normalized',  ['nir', 'green'],   6),
    'NDBI': ('Normalized',  ['swir', 'nir'],    6),
}

# Set elements for naming files
nameids = {
    '[imsys]': 3,
    '[sat]': 3,
    '[place]': 6,
    '[date]': 8,
    '[year]': 4,
    '[month]': 2,
    '[day]': 2,
}

# Set dictionary of modules to get metadata from different sources
metalib = {
    'LST': landsat,
    'PLN': planet,
}

temp_dir_list = tdir(default_temp)

# Conversts non-list objects to a list of length 1
def obj2list(obj):
    if isinstance(list, obj):
        return obj
    else:
        return [obj]

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

# Gets Landsat metadata value by key
def get_meta_landsat(path, call):
    mtl = open(path).read()
    mtl_list = re.split('  ', mtl)
    for i in range(len(mtl_list)):
        mtl_list[i] = mtl_list[i].strip()
    while '' in mtl_list:
        mtl_list.remove('')
    for i in range(len(mtl_list)):
        if re.search('.+ = .+', mtl_list[i]) is not None:
            key = re.search('.+ =', mtl_list[i]).group()[:-2]
            if key in ['GROUP', 'END_GROUP']:
                continue
            if key == call:
                val = re.search('= .+', mtl_list[i]).group()[2:]
                try:
                    val = float(val)
                except:
                    if (val.startswith('"') and val.endswith('"')):
                        val = val[1:-1]
    return val

# Reads Sentinel metadata
def get_meta_sentinel(path, call, check=None, data='text', attrib=None, sing_to_sing=True, digit_to_float=True, mtd=False):
    if mtd:
        path = os.path.split(path)[0] + r'\GRANULE'
        folder_mtd = os.listdir(path)[0]
        path = path + '\\' + folder_mtd + r'\MTD_TL.xml'
    try:
        iter = iter_list(et.parse(path).getroot(), call)
        result = iter_return(iter, data, attrib)
        if check is not None:
            filter = attrib_filter(iter, check)
            result = list(np.array(result)[filter])
        result = sing2sing(result, sing_to_sing, digit_to_float)
    except:
        raise Exception(('Cannot open file: ' + path))
    return result

# Defines image system by path to file or returns None if no one matches
def get_imsys(path):
    if os.path.exists(path):
        for imsys, module in globals()['imsys_dict']:
            file = os.path.split(path)[1]
            if check_name(file, module.imsys_data.template):
                return imsys
    else:
        print('Path does not exist: {}'.format(path))
    return None

# Class containing image processing parameters and procedures
class process(object):

    def __init__(self,
                 output_path=globals()['default_output'],
                 image_system = globals()['image_system_list'],
                 work_method = globals()['work_method_list'][0],
                 tdir = globals()['default_temp']):

        self.output_path = output_path  # must be dir
        #self.work_method = work_method
        #self.input = []
        self.scenes = []  # contains available scenes
        self.options = {}
        self.tdir = tdir

    def __str__(self):
        return 'Process of scenes available.'.format(len(self.scenes))

    # Returns number of paths in the input_list
    def __len__(self):
        return len(self.scenes)

    # Checks if a single path is available in the input_list
    def __bool__(self):
        return bool(self.scenes)

    # Adds new path to self.input_list
    def add_scene(self, path2scene):
        #newscene = scene(path2scene)
        try:
            newscene = scene(path2scene)
        #except FileNotFoundError:
        except IOError:
            print('Cannot open scene by path: {}'.format(path2scene))
            newscene = None
        if newscene is not None:
            self.scenes.append(newscene)
        return self

    def input(self, path, search_scenes = True):
        path = listoftype(path, str)
        #print('Path: {}'.format(path))
        if path is None:
            return self
        for path2scene in path:
            file = os.path.isfile(path2scene)
            if file:
                self.add_scene(path2scene)
            if search_scenes:
                if file:
                    path2folder = os.path.split(path2scene)[0]
                else:
                    path2folder = path2scene
                    #print('Path to folder: {}'.format(path2folder))
                input_list = walk_find(path2folder, globals()['corner_file_list'].values())
                #print('Input list: {}'.format(input_list))
                for newpath2scene in input_list:
                    self.add_scene(newpath2scene)
        return self

# Every space image scene
class scene:

    def __init__(self, path, imsys):

        if not os.path.exists(path):
            print('Path does not exist: {}'.format(path))
            # raise FileNotFoundError
            raise IOError

        module = globals()['imsys_dict'].get(imsys)
        if module is None:
            print('Unknown data source: {}'.format(imsys))
            raise KeyError

        meta = module.metadata(path, module.imsys_data)
        if not meta.check():
            raise ImportError

        self.fullpath = path
        folder, file = os.path.split(path)
        self.path = self.filepath = folder
        self.file = file
        self.files = self.meta.files
        self.imsys = imsys
        self.meta = meta
        self.clip_parameters = {}

    def __bool__(self):
        return bool(self.fullpath)

    # Get path to raster data file. Returns None if the clipped file hasn't been created
    def get_raster_local_path(self, file_id):
       return fullpath(self.filepath, self.meta.get_raster_path(file_id))

    # Get raster path by file id. Clip raster file if necessary
    def get_raster_path(self, file_id):

        file_id = str(file_id)
        if not file_id in self.files:
            if file_id in self.meta.files:
                path2file = self.clipraster(file_id)
            else:
                print('Unknown file id: {}'.format(file_id))
                return None
        else:
            path2file = self.get_raster_local_path(file_id)

        return path2file

    # Clips a single raster
    def clipraster(self, file_id):

        file_id = str(file_id)
        full_export_path = self.get_raster_local_path(file_id)
        export_folder = os.path.split(full_export_path)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        geodata.clip_raster(path2raster = fullpath(self.path, self.meta.get_raster_path(file_id)),
                            path2vector = self.clip_parameters.get('path2vector'),
                            export_path = full_export_path,
                            byfeatures = self.clip_parameters.get('byfeatures', True),
                            exclude = self.clip_parameters.get('exclude', False),
                            nodata = self.clip_parameters.get('nodata', 0))

        self.files.append(file_id)

        return full_export_path

    # Gets path to raster file containing th bands and its number
    def get_band_path(self, band_id):

        band_id = str(band_id)
        band_tuple = self.meta.bandpaths.get(band_id)
        if band_tuple is not None:
            raster_path = self.get_raster_path(band_tuple[0])
        else:
            print('Unknown band_id: {}'.format(band_id))
            return None
        if raster_path is not None:
            return (raster_path, band_tuple[1])

        return (raster_path, band_tuple[1])

    # Creates a copy of a scene, cropping the original data with shpapefile
    def clip(self, path2vector, export_path = None, byfeatures = True, exclude = False, nodata = 0, save_files = False):

        if export_path is None:
            export_path = temp_dir_list.create()

        self.filepath = export_path
        self.files = []
        self.clip_parameters['path2vector'] = path2vector
        self.clip_parameters['byfeatures'] = byfeatures
        self.clip_parameters['exclude'] = exclude
        self.clip_parameters['nodata'] = nodata

        if save_files:
            for key in self.meta.filepaths:
                self.clipraster(key)

        return None

    # Aborts clipping scene, the created files aren't deleted
    def unclip(self):
        self.filepath = self.path
        self.filenames = self.meta.filenames
        self.clip_parameters = {}
        return None

    # Creates a composite of a single scene --- change
    def composite(self, bands, export_path, main_band = None, exclude_nodata = True, enforce_nodata = None):

        path2start = []
        band_nums = []

        for band_id in bands:
            raster_path, band_num = self.get_band_path(band_id)
            path2start.append(raster_path)
            band_nums.append(band_num)

        if main_band is None:
            path2target = path2start[0]

        else:
            path2target = self.get_band_path(main_band)[0]

        geodata.raster2raster(path2start, path2target, export_path, band_nums = band_nums, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata)

        return None

    # Creates default composite by name ('RGB', 'NIR', etc.)
    def default_composite(self, comptype, export_path, main_band = None, exclude_nodata = True, enforce_nodata = None):

        compdict = globals()['composites_dict']

        if comptype in compdict:
            try:
                self.composite(compdict[comptype], export_path, main_band = main_band, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata)
            except:
                print('Cannot make composite: {}'.format(comptype))
        else:
            print('Unknown composite: {}'.format(comptype))

        return None

    # Calculates index by id
    def calculate_index(self, index_id, export_path):

        index_params = globals()['index_dict'].get(index_id)

        if index_params is not None:
            funcid, bandlist, dt = index_params
            func = geodata.index_calculator.get(funcid)
            bandpath_list = []

            for band_id in bandlist:
                bandpath_list.append(self.get_band_path(band_id))

            if (func is not None) and (not None in bandpath_list):
                #func(bandpath_list, export_path, dt=dt)
                try:
                    func(bandpath_list, export_path)
                    pass
                except:
                    print('Error calculating {}'.format(index_id))
            else:
                print('Insuffisient parameters for {} calculation'.format(index_id))

        return None

def timecomposite(scenes, band_ids, scene_nums, export_path, path2target = None, exclude_nodata = True):

    path2start = []
    band_nums = []
    assert len(band_ids) == len(scene_nums)

    for i, band_id in enumerate(band_ids):
        raster_path, band_num = scenes[scene_nums[i]].get_band_path(band_id)
        path2start.append(raster_path)
        band_nums.append(band_num)

    #print(path2start)
    if path2target is None:
        path2target = path2start[0]

    geodata.raster2raster(path2start, path2target, export_path, band_nums = band_nums, exclude_nodata = exclude_nodata)

    return None
