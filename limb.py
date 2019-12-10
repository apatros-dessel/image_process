# Auxilliary functions for image processor

import os
import re
import numpy as np
from collections import OrderedDict

default_temp = '{}\image_processor'.format(os.environ['TMP'])
if not os.path.exists(default_temp):
    os.makedirs(default_temp)

# Returns a string of proper length cutting the original string and stretching it adding filler symbols if necessary
def stringoflen(value, length, filler = '0', left = False):
    value = str(value)[:length]
    dif = length - len(value)
    if dif > 0:
        if left:
            value = filler[0] * dif + value
        else:
            value = value + filler[0] * dif
    return value

# Creates a list of predefined lenghth filled with value
def listfull(length, value=1):
    newlist = []
    for i in range(length):
        newlist.append(value)
    return newlist

# Converts objects into a list or tuple of objects of specific type
def listoftype(obj, objtype, export_tuple = False):
    if isinstance(obj, objtype):
        return [obj]
    elif isinstance(obj, tuple):
        obj = list(obj)
    if isinstance(obj, list):
        for i in range(len(obj)-1, -1, -1):
            if not isinstance(obj[i], objtype):
                obj.pop(i)
    else:
        print('Error listing object of type: {}'.format(type(obj)))
        return None
    if export_tuple:
        obj = tuple(obj)
    return obj

# Converts all values in list into integers. Non-numeric values're converted to zeros
def intlist(list_):
    for val in range(len(list_)):
        try:
            list_[val] = int(list_[val])
        except:
            list_[val] = 0
    return list_

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

# Returns a new dictionary filtered by key values
def slice_orderdict(dict, call, include = True, delete_call = False):
    call = str(call)
    include = bool(include)
    delete_call = bool(delete_call)
    orderdict = OrderedDict()
    for key in dict:
        if (call in key) is include:
            if delete_call:
                orderdict[key.replace(call, '')] = dict[key]
            else:
                orderdict[key] = dict[key]
    return orderdict

def fill_orderdict(key_list, value):
    result = OrderedDict()
    for key in key_list:
        result[key] = value
    return result

def list_orderdict(dict_tuple, newvals2tuples = False):
    dict_tuple = tuple(dict_tuple)
    result = OrderedDict()
    if len(dict_tuple) > 0:
        keys = dict_tuple[0].keys()
        for key in keys:
            newval = []
            for dict_ in dict_tuple:
                newval.append(dict_.get(key))
            if newvals2tuples:
                newval = tuple(newval)
            result[key] = newval
    return result

# Create fullpath from folder, file and extension
def fullpath(folder, file, ext=None):
    if ext is None:
        ext = ''
    else:
        ext = ('.' + str(ext).replace('.', ''))
    return r'{}\{}{}'.format(folder, file, ext)

# Creates new path
def newname(folder, ext = None):
    if os.path.exists(folder) and os.path.isdir(folder):
        i = 0
        path_new = fullpath(folder, i, ext)
        while os.path.exists(path_new):
            i += 1
            path_new = fullpath(folder, i, ext)
        return path_new
    else:
        return None

# Creates new empty dir
def newdir(path):
    new_path = newname(path)
    if (new_path is not None) and not os.path.exists(new_path):
        os.mkdir(new_path)
        return new_path
    else:
        return None

# Removes all files in the directory
def cleardir(path):
    files = os.listdir(path)
    errors = []
    for file in files:
        try:
            os.remove(fullpath(path, file))
        except:
            errors.append(file)
    return not bool(errors)

# Check correctness of file name
def check_name(name, pattern):
    search = re.search(pattern, name)
    if search is None:
        return False
    else:
        return True

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
def walk_find(path, templates, id_max=10000):
    templates = listoftype(templates, str, export_tuple=True)
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
                for template in templates:
                    #print('{}: \n {} \n'.format(template, file_n))
                    if check_name(file_n, template):
                        export_.append(file_n)
        id += 1
    if len(path_list) > id_max:
        raise Exception('Number of folder exceeds maximum = {}'.format(id_max))
    return export_

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

# Works with temporary directories
class tdir():

    def __init__(self, tempdir = None):
        if tempdir is None:
            tempdir = globals()['default_temp']
        self.corner = newdir(tempdir)
        if self.corner is not None:
            self.paths = []

    def __len__(self):
        return len(self.paths)

    # Creates a new tempdir
    def create(self):
        path_new = newdir(self.corner)
        if path_new is not None:
            self.paths.append(path_new)
            return path_new
        else:
            return None

    # Deletes tempdir by number
    def clear(self, i=None):
        if i is None:
            i = len(self)-1
        try:
            if cleardir(self.paths[i]):
                os.rmdir(self.paths[i])
                self.paths.pop(i)
                return True
            else:
                return False
        except:
            return False

    # Deletes all tempdirs
    def empty(self):
        fin = True
        for i in range(len(self)-1, -1, -1):
            try:
                self.clear()
            except:
                fin = False
        return fin

    # Deletes all data when the interpreter is closed
    def __del__(self):
        try:
            if self.empty() and cleardir(self.corner):
                os.rmdir(self.corner)
        except:
            pass

    # Create path to a new file

def scroll(obj):
    if hasattr(obj, '__iter__'):
        if isinstance(obj, (dict)):
            for val in obj:
                print('{}: {}'.format(val, obj[val]))
        else:
            for val in obj:
                print(val)
    else:
        print(obj)

# Landsat-8 metadata
class landsat_8:

    def __init__(self, path):
        folder, file = os.path.split(path)
        if check_name(file, globals()['filepattern']['LS8']):
            self.files = globals()['bands']['LS8']
            self.bands = globals()['bands']['LS8']
            self.mtl = mtl2orderdict(path)
            self.filenames = slice_orderdict(self.mtl, 'FILE_NAME_BAND_', delete_call = True)
            self.bandpaths = list_orderdict([self.filenames, fill_orderdict(self.filenames, 1)])
            year, month, day = intlist(self.mtl.get('DATE_ACQUIRED').split('-'))
            self.date = dtime.date(year, month, day)
            self.place = file[10:16]
        else:
            print('Wrong file name: {}'.format(file))

# Planet metadata
class planet:

    def __init__(self, path):
        folder, file = os.path.split(path)
        if check_name(file, globals()['filepattern']['PLN']):
            self.files = {'Analytic': 'Analytic', 'DN': 'mask'}
            self.bands = globals()['bands']['PLN']
            self.xmltree = xml2tree(path)
            self.filenames = getplanetfiles(self.xmltree)
            self.bandpaths = OrderedDict({'1': ('Analytic', 1), '2': ('Analytic', 2), '3': ('Analytic', 3), '4': ('Analytic', 4)})
            aq_date_time = get_from_tree(self.xmltree, 'acquisitionDateTime')
            year, month, day = intlist(aq_date_time[:10].split('-'))
            self.date = dtime.date(year, month, day)
            self.place = file[:15]
        else:
            print('Wrong file name: {}'.format(file))

# Scene metadata
class scene_metadata:

    def __init__(self, path, template):
        if check_name(path, template):
            self.imsys = None                       # Image system (Landsat, Sentinel, etc.) as str of length 3
            self.sat = None                         # Satellite id (Landsat-8, Sentinel-2A, 0e26 (Planet id), etc.) as str
            self.container = {}                     # Place to keep source metadata as a dictionary
            self.files = OrderedDict()              # Dictionary of file ids
            self.filepaths = OrderedDict()          # Dictionary of filepaths
            self.bands = OrderedDict()              # Dictionary of bands
            self.bandpaths = OrderedDict()          # Dictionary of paths to bands (each path is a tuple of file id as str and band number as int)
            self.datetime = None                    # Datetime as datetime
            self.location = {}                      # Image locationa data as str
            self.datamask = None                    # Local path to data mask as vector file
            self.cloudmask = None                   # Local path to cloud mask as vector file
        else:
            del self

    # Get local path to raster file
    def get_raster_path(self, file_id):
        file_num = self.files.get(file_id)
        if file_num is not None:
            raster_path = self.filepaths.get(file_num)
        else:
            print('Unknown file_id: {}'.format(file_id))
            return None
        if raster_path is None:
            print('Path not found for file_num {}'.format(file_num))
        else:
            return raster_path

    # Get local path to raster file containing specified band and
    def get_band_path(self, band_id):
        band_tuple = self.bandpaths.get(band_id)
        if band_tuple is not None:
            #file_id, band_num = band_tuple
            raster_path = self.get_raster_path(band_tuple[0])
        else:
            print('Unknown band_id: {}'.format(band_id))
            return None
        if raster_path is not None:
            return (raster_path, band_tuple[1])

    # Get