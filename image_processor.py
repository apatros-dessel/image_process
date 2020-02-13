# Version 0.3

from tools import *

import geodata

# import mylandsat
import myplanet
import mykanopus
import mysentinel

# Constants


default_output = os.getcwd() # default output directory for a process

metalib = {
    # 'LST': mylandsat,
    'SNT': mysentinel,
    'PLN': myplanet,
    'KAN': mykanopus,
}

# A dictionary of metadata filenames templates
template_dict = {}
for key in metalib:
    template_dict[key] = metalib[key].templates

'''
template_dict = {
    imsys1_name: (template1, template2, ),
    imsys2_name: (template1, template2, template3, ),
    ... etc. ...
}
'''

#scroll(template_dict)

'''
-- keeping here until new modules will be made

# Set image systems available for analysis
image_system_list = [
    'LST',                  # LANDSAT
    'SNT',                  # SENTINEL
    'PLN',                  # PLANET
    'KAN',                  # KANOPUS
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
    'RGBN':     ['red', 'green', 'blue', 'nir']     # Four channels for image classification
}

# Set default types of indices
index_dict = {
    'NDVI': ('Normalized',  ['nir', 'red'],     6,  'Reflectance'),
    'NDWI': ('Normalized',  ['nir', 'green'],   6,  'Reflectance'),
    'NDBI': ('Normalized',  ['swir', 'nir'],    6,  'Reflectance'),
}

# Set elements for naming files
nameids = {
    '[imsys]':  3,
    '[sat]':    3,
    '[place]':  6,
    '[date]':   8,
    '[year]':   4,
    '[month]':  2,
    '[day]':    2,
}

# Product types list
product_types_list = [
    'Radiance',
    'Reflectance'
]

# Product types for work and GDAL datatypes for them
raster_product_types = {
    'Radiance':     7,
    'Reflectance':  7,
}

# Defines image system by path to file or returns None if no one matches
def get_imsys(path):
    if os.path.exists(path):
        for imsys, module in globals()['metalib']:
            file = os.path.split(path)[1]
            if check_name(file, module.template):
                return imsys
    else:
        print('Path does not exist: {}'.format(path))
    return None

# Returns product generation function
def get_product_generation_function(imsys, prodid):

    func = globals()['metalib'].get(imsys).product_func.get(prodid)

    if hasattr(func, '__repr__'):
        return func

    else:
        print('"{}" product function not found for "{}"'.format(prodid, imsys))
        return None

temp_dir_list = tdir(default_temp) # tdir object for working with temporary files

# Class containing image processing parameters and procedures
class process(object):

    def __init__(self,
                 output_path=globals()['default_output'],
                 #image_system = globals()['image_system_list'],
                 #work_method = globals()['work_method_list'][0],
                 tdir = globals()['default_temp']):

        self.output_path = output_path  # must be dir
        #self.work_method = work_method
        #self.input = []
        self.scenes = []  # contains available scenes
        self.options = {}
        self.tdir = tdir

    def __str__(self):
        return 'Process of {} scenes available'.format(len(self.scenes))

    # Returns number of paths in the input_list
    def __len__(self):
        return len(self.scenes)

    # Checks if a single path is available in the input_list
    def __bool__(self):
        return bool(self.scenes)

    # Adds new path to self.input_list
    def add_scene(self, newpath, imsys):
        #newscene = scene(path2scene)
        print(newpath)
        try:
            newscene = scene(newpath, imsys)
        #except FileNotFoundError:
        except IOError:
            print('Cannot open {} scene by path: {}'.format(imsys, newpath))
            newscene = None
        if newscene is not None:
            self.scenes.append(newscene)
        return self

    def input(self, path, imsys_list = None):
        path = listoftype(path, str)
        # print('Path: {}'.format(path))
        if path is None:
            return self
        if imsys_list is None:
            imsys_list = globals()['template_dict'].keys()
        # print(imsys_list)
        for path2scene in path:
            file = os.path.isfile(path2scene)
            if file:
                fin = False
                for imsys in imsys_list:
                    if fin:
                        break
                    templates = globals()['template_dict'].get(imsys)
                    # print(templates)
                    if templates is not None:
                        for template in templates:
                            # print(template)
                            if re.search(template, path2scene) is not None:
                                # print(re.search(template, path2scene).group())
                                self.add_scene(path2scene, imsys)
                                fin = True
                                break
            else:
                input_list = walk_find(path2scene, globals()['template_dict'].keys(), globals()['template_dict'].values())
                # scroll('Input list: {}'.format(input_list))
                if (input_list is not None) and len(input_list)>0:

                    for newpath2scene in input_list:
                        # print(newpath2scene)
                        newpath, imsys = newpath2scene

                        # Filter scenes by imsys
                        if imsys not in imsys_list:
                            continue

                        self.add_scene(newpath, imsys)
        return self

    def get_dates(self):
        dates_list = []
        for ascene in self.scenes:
            # print(ascene.meta.datetime.date())
            scene_date = ascene.meta.datetime.date()
            if scene_date not in dates_list:
                dates_list.append(scene_date)
        dates_list.sort()
        return dates_list

    def get_paths(self):
        paths_dict = OrderedDict()
        for ascene in self.scenes:
            paths_dict[ascene.meta.id] = ascene.path
        return paths_dict

    # Returns a dictionary of scene covers shapefiles list
    def get_cover_paths(self):
        covers_dict = OrderedDict()
        for ascene in self.scenes:
            datamask = ascene.datamask()
            if datamask is not None:
                covers_dict[ascene.meta.id] =  fullpath(ascene.path, datamask)
            else:
                print('Datamask not found for {}'.format(ascene.meta.id))
        return covers_dict

    def get_vector_cover(self, vector_cover_name, report_name=None):

        path2vector_list = []
        report = OrderedDict()

        for ascene in self.scenes:
            # print(ascene.meta.datamask)
            path2vector_list.append(fullpath(ascene.path, ascene.meta.datamask))
            # path2vector_list.append(ascene.meta.datamask)
            rep_row = OrderedDict()
            rep_row['datamask'] = path2vector_list[-1]
            report[ascene.meta.id] = rep_row

        if report_name is not None:
            try:
                dict_to_xls(fullpath(self.output_path, report_name), report)
            except:
                print('Unable to export data as xls')
                scroll(report)
        print(fullpath(self.output_path, vector_cover_name))
        geodata.JoinShapesByAttributes(path2vector_list, fullpath(self.output_path, vector_cover_name), geom_rule=1, attr_rule=0)

        return None

# Every space image scene
class scene:

    def __init__(self, path, imsys):

        if not os.path.exists(path):
            print('Path does not exist: "{}"'.format(path))
            # raise FileNotFoundError
            raise IOError

        module = globals()['metalib'].get(imsys)
        if module is None:
            print('Unknown data source: {}'.format(imsys))
            raise KeyError

        meta = module.metadata(path)

        if not meta.check():
            raise ImportError

        self.fullpath = path
        folder, file = os.path.split(path)
        self.path = self.filepath = folder

        self.meta = meta

        self.file = file
        self.files = self.meta.files
        self.imsys = imsys
        self.clip_parameters = {}

        self.products = {}

    def __bool__(self):
        return bool(self.fullpath)

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
            path2file = fullpath(self.filepath, self.meta.get_raster_path(file_id))

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
                            nodata = self.clip_parameters.get('nodata', 0),
                            compress = self.clip_parameters.get('compress'))

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

    def get_product_path(self, prod_id, band_id, set_product_path = None, set_name = None):

        if prod_id not in globals()['product_types_list']:
            print('Unknown product type: {}'.format(prod_id))
            return None

        if prod_id not in self.products:
            self.products[prod_id] = {}

        if band_id in self.products[prod_id]:

            prod_name, prod_bandnum =  self.products[prod_id][band_id]
            prod_path = (r'{}\{}'.format(set_product_path, prod_name))

        else:

            prod_func = get_product_generation_function(self.imsys, prod_id)

            if prod_func is None:
                return None

            if set_product_path is None:
                set_product_path = temp_dir_list.create()

            if set_name is None:
                prod_name = r'[id]_{}_{}.tif'.format(band_id, prod_id)
            else:
                prod_name = set_name

            prod_name = self.meta.name(prod_name)
            prod_path = (r'{}\{}'.format(set_product_path, prod_name))
            prod_bandnum = 1

            prod_func(self.get_band_path(band_id), band_id, (prod_path, prod_bandnum), self.meta, dt = globals()['raster_product_types'].get(prod_id))

            self.products[prod_id][band_id] = (prod_name, prod_bandnum)

        return (prod_path, prod_bandnum)

    # Creates a copy of a scene, cropping the original data with shpapefile
    def clip(self, path2vector, export_path = None, byfeatures = True, exclude = False, nodata = 0, save_files = False, compress = None):

        if export_path is None:
            export_path = temp_dir_list.create()

        self.filepath = export_path
        self.files = []
        self.clip_parameters['path2vector'] = path2vector
        self.clip_parameters['byfeatures'] = byfeatures
        self.clip_parameters['exclude'] = exclude
        self.clip_parameters['nodata'] = nodata
        self.clip_parameters['compress'] = compress

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

    def datamask(self):
        if self.meta.datamask is not None:
            return self.meta.datamask
        else:
            return None

    # Creates a composite of a single scene --- change
    def composite(self, bands, export_path, path2target = None, exclude_nodata = True, enforce_nodata = None, compress = None, overwrite = True):

        bandpaths = []
        for band_id in bands:
            bandpaths.append(self.get_band_path(band_id))

        # scroll(bandpaths)

        try:
            res = geodata.raster2raster(bandpaths, export_path, path2target = path2target, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata, compress = compress, overwrite=overwrite)
        except:
            print('Error making composite for: {}'.format(export_path))
            return 1

        return res

    # Creates default composite by name ('RGB', 'NIR', etc.)
    def default_composite(self, comptype, export_path, path2target = None, exclude_nodata = True, enforce_nodata = None, compress = None, overwrite = True):

        compdict = globals()['composites_dict']

        if comptype in compdict:
            # self.composite(compdict[comptype], export_path, path2target=path2target, exclude_nodata=exclude_nodata, enforce_nodata=enforce_nodata, compress = compress)
            try:
                res = self.composite(compdict[comptype], export_path, path2target=path2target, exclude_nodata=exclude_nodata, enforce_nodata=enforce_nodata, compress = compress, overwrite=overwrite)
                if res == 0:
                    print('{} composite saved: {}'.format(comptype, export_path))
                return res
            except:
                print('Cannot make composite: {} for scene {}'.format(comptype, self.meta.id))
                return 1
        else:
            print('Unknown composite: {}'.format(comptype))
            return 1

    # Calculates index by id
    def calculate_index(self, index_id, export_path, name = None, compress = None, overwrite = True):

        index_params = globals()['index_dict'].get(index_id)

        if index_params is not None:
            funcid, bandlist, dt, prod_id = index_params
            func = geodata.index_calculator.get(funcid)
            bandpath_list = []

            for band_id in bandlist:
                # bandpath_list.append(self.get_band_path(band_id))
                bandpath_list.append(self.get_product_path(prod_id, band_id, set_product_path=export_path, set_name=name))

            if (func is not None) and (not None in bandpath_list):
                #func(bandpath_list, export_path, dt=dt)
                try:
                    res = func(bandpath_list, export_path, dt=dt, compress = compress, overwrite=overwrite)
                    if res == 0:
                        print('Index raster file saved: {}'.format(export_path))
                    return res
                except:
                    print('Error calculating {} to {}'.format(index_id, export_path))
                    return 1
            else:
                print('Insuffisient parameters for {} calculation'.format(index_id))
                return 1

def timecomposite(scenes, band_ids, scene_nums, export_path, path2target = None, exclude_nodata = True, compress = None):

    assert len(band_ids) == len(scene_nums)

    bandpaths = []
    for i, band_id in enumerate(band_ids):
        bandpaths.append(scenes[scene_nums[i]].get_band_path(band_id))
    # scroll(bandpaths)

    try:
        res = geodata.raster2raster(bandpaths, export_path, path2target = path2target, exclude_nodata = exclude_nodata, compress = compress)
        if res == 0:
            print('Time composite saved: {}'.format(export_path))
    except:
        print('Error saving timecomposite: {}'.format(export_path))
        return 1

    return res

