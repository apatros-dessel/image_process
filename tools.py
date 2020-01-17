# Auxilliary functions for image processor

import os
import re
import numpy as np
from collections import OrderedDict
import xml.etree.ElementTree as et
import xlwt
from datetime import datetime
from copy import deepcopy

default_temp = '{}\image_processor'.format(os.environ['TMP'])

if not os.path.exists(default_temp):
    os.makedirs(default_temp)

# Function always returning None
def returnnone(obj):
    return None

# Function always returning object
def returnobj(obj):
    return obj

# Check existance of file
def check_exist(path, ignore=False):
    if not ignore:
        if os.path.exists(path):
            print('The file already exists: {}'.format(path))
            return True
    return False

# Conversts non-list objects to a list of length 1
def obj2list(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]

# Repeats th last value in the list until it has the predefined length
def list_of_len(list_, len_):
    while len(list_) < len:
        list_.append(list_[-1])
    return list_

# Returns list with excluded values
def list_ex(list_, exclude_):
    exclude_ = obj2list(exclude_)
    for i in range(len(list_)-1, -1, -1):
        if (list_[i] in exclude_):
            list_.pop(i)
    return list_

def lget(iter_obj, id, id2=None):
    if id2 is not None:
        val = iter_obj[id, id2]
        if len(val) == 0:
            val = iter_obj[-1:]
    else:
        try:
            val = iter_obj[id]
        except IndexError:
            val = iter_obj[-1]
    return val

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

# Returns a new dictionary with all values with unique keys and sum of values with different keys
def sumdict(a, b):
    assert isinstance(a, dict) and isinstance(b, dict)
    if isinstance(a, OrderedDict) or isinstance(b, OrderedDict):
        c = OrderedDict()
    else:
        c = dict()
    keys = list(a.keys())
    for newkey in b.keys():
        if newkey not in keys:
            key.append(newkey)
    for key in keys:
        vals = [a.get(key), b.get(key)]
        if vals[0] is None:
            c[key] = vals[1]
        elif vals[1] is None:
            c[key] = vals[0]
        else:
            try:
                c[key] = vals[0] + vals[1]
            except:
                c[key] = vals
        return c

# Create fullpath from folder, file and extension
def fullpath(folder, file, ext=None):
    if ext is None:
        ext = ''
    else:
        ext = ('.' + str(ext).replace('.', ''))
    return r'{}\{}{}'.format(folder, file, ext)

# Creates new path
def newname(folder, ext = None):
    # print(os.path.exists(folder), folder)
    # print(os.path.isdir(folder))
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
def walk_find(path, ids_list, templates_list, id_max=10000):
    #templates_list = listoftype(templates_list, str, export_tuple=True)
    if os.path.exists(path):
        if not os.path.isdir(path):
            path = os.path.split(path)[0]
        path_list = [path]
        path_list = [path_list]
    else:
        print('Path does not exist: {}'.format(path))
        return None
    id = 0
    export_ = []
    while id < len(path_list) < id_max:
        for id_fold in range(len(path_list[id])):
            fold_, file_ = fold_finder(path_list[id][id_fold])
            if fold_ != []:
                path_list.append(fold_)
            for file_n in file_:
                for i, templates in enumerate(templates_list):
                    #print('{}: \n {} \n'.format(template, file_n))
                    for template in templates:
                        if check_name(file_n, template):
                            export_.append((file_n, ids_list[i]))
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
            if digit_to_float and obj.isdigit():
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

def winprint(obj, decoding = None):
    if decoding is not None:
        try:
            print(obj.decode(decoding))
            return None
        except:
            print('Error decoding: "{}"'.format(decoding))
    print(obj)
    return None

def scroll(obj, print_type=True, decoding=None):
    if print_type:
        print('Object of {}:'.format(type(obj)))
    if hasattr(obj, '__iter__'):
        if len(obj) == 0:
            print('  <empty>')
        elif isinstance(obj, (dict, OrderedDict)):
            for val in obj:
                winprint('  {}: {}'.format(val, obj[val]), decoding=decoding)
        else:
            for val in obj:
                winprint('  {}'.format(val), decoding=decoding)
    else:
        winprint('  {}'.format(obj), decoding=decoding)

# Reads .xml file and returns metadata as element tree
def xml2tree(path):
    try:
        return et.parse(path)
    except:
        raise Exception(('Cannot open file: ' + path))

# Converts data from a root call to a list
def iter_list(root, call):
    iter_list = []
    for obj in root.iter():
        if call in obj.tag:
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

# Returns dict values as a list
def mdval(dict_):
    return list(dict_.values())[0]

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

# Gets metadata from xml tree
def get_from_tree(xml_tree, call, check=None, data='text', attrib=None, sing_to_sing=True, digit_to_float=True):
    if (attrib is not None):
        data = 'attrib'
    iter = iter_list(xml_tree, call)
    result = iter_return(iter, data, attrib)
    if check is not None:
        filter = attrib_filter(iter, check)
        result = list(np.array(result)[filter])
    #scroll(sing2sing(result, sing_to_sing, digit_to_float))
    return sing2sing(result, sing_to_sing, digit_to_float)

# Export data to xls
def dict_to_xls(path2xls, adict): # It's better to use OrderedDict to preserve the order of rows and columns

    wb = xlwt.Workbook()
    ws = wb.add_sheet('New_Sheet')

    # Find all column names
    col_list = ['']
    for row_key in adict:
        for key in adict.get(row_key).keys():
            if not key in col_list:
                col_list.append(key)

    # Write column names
    row = ws.row(0)
    for col_num, col_name in enumerate(col_list):
        row.write(col_num, col_name)

    # Write data
    for id, row_key in enumerate(adict):
        row_num = id+1
        row = ws.row(row_num)
        rowdata = adict.get(row_key)
        if isinstance(rowdata, dict):
            row.write(0, row_key)
            for key in rowdata:
                row.write(col_list.index(key), rowdata.get(key))
        elif hasattr(rowdata, '__iter__'):
            row.write(0, row_num)
            for col_id, obj in enumerate(rowdata):
                row.write(col_id+1, obj)
        else:
            row.write(0, row_num)
            row.write(1, rowdata)

    wb.save(path2xls)

    return None

# Image system data object
class imsys_data:

    def __init__(self, imsys, template):

        if not isinstance(imsys, str):
            print('Wrong imsys data type: str is needed')
            raise TypeError

        if len(imsys) != 3:
            print('Length of imsys was incorrect, reduced to 3')
            imsys = stringoflen(imsys.strip(), 3)

        if not isinstance(template, str):
            print('Wrong template data type: str is needed')
            raise TypeError

        self.imsys = imsys
        self.template = template
        self.files = []
        self.bandpaths = OrderedDict()

# Scene metadata
class scene_metadata:

    def __init__(self, imsys):
        self.imsys = imsys       # Image system (Landsat, Sentinel, etc.) as str of length 3

        self.container = {}                     # Place to keep source metadata as a dictionary. Filled by the imsys-specific function

        self.sat = None                         # Satellite id (Landsat-8, Sentinel-2A, 0e26 (Planet id), etc.) as str
        self.id = None,                         # A unique scene identifier
        self.lvl = None,                        # Data processing level
        self.files = OrderedDict()              # Dictionary of file ids
        self.filepaths = OrderedDict()          # Dictionary of filepaths
        self.bands = OrderedDict()              # Dictionary of bands
        self.bandpaths = OrderedDict()          # Dictionary of paths to bands (each path is a tuple of file id as str and band number as int)
        self.datetime = None                    # Datetime as datetime
        self.location = {}                      # Image locationa data as str
        self.datamask = None                    # Local path to data mask as vector file
        self.cloudmask = None                   # Local path to cloud mask as vector file
        self.namecodes = {'[imsys]': imsys}     # Codes for names to products

    def check(self):
        check_list = OrderedDict({
            'imsys':        self.imsys is not None,
            'container':    len(self.container) > 0,
            'sat':          self.sat is not None,
            'id':           isinstance(self.id, str),
            'lvl':          self.lvl is not None,
            'files':        len(self.files) > 0,
            'filepaths':    len(self.filepaths) > 0,
            #'bands':       len(self.bands) > 0,
            'bandpaths':    len(self.bandpaths) > 0,
            'datetime':     isinstance(self.datetime, datetime),
            'namecodes':    len(self.namecodes) > 0,
        })
        if False in check_list.values():
            error_keys = np.array(list(check_list.keys()))[~ np.array(list(check_list.values()))]
            for key in error_keys:
                print('Error in key: {} == {}'.format(key, check_list[key]))
            return False
        else:
            return True


    def write_time_codes(self, datetime=None):

        if datetime is None:
            datetime = self.datetime

        if datetime is not None:

            datetime_string = '{}{}{}_{}{}{}'.format(
                stringoflen(self.datetime.year, 4, left=True),
                stringoflen(self.datetime.month, 2, left=True),
                stringoflen(self.datetime.day, 2, left=True),
                stringoflen(self.datetime.hour, 2, left=True),
                stringoflen(self.datetime.minute, 2, left=True),
                stringoflen(self.datetime.second, 2, left=True),
            )

            datetime_codes = {
                '[datetime]': datetime_string,
                '[date]': datetime_string[:8],
                '[year]': datetime_string[:4],
                '[month]': datetime_string[4:6],
                '[day]': datetime_string[6:8],
                '[time]': datetime_string[9:],
                '[hour]': datetime_string[9:11],
                '[minute]': datetime_string[11:13],
                '[second]': datetime_string[13:15],
            }

            self.namecodes.update(datetime_codes)

        else:
            print('No datetime data found')

        return None

    # Get local path to raster file
    def get_raster_path(self, file_id):
        if file_id in self.files:
            raster_path = self.filepaths.get(file_id)
        else:
            print('Error: file_id not found: {}'.format(file_id))
            return None
        if raster_path is None:
            print('Error: path not found for file_num {}'.format(file_id))
        else:
            return raster_path

    # Get local path to raster file containing specified band and
    def get_band_path(self, band_id):
        band_tuple = self.bandpaths.get(band_id)
        if band_tuple is not None:
            #file_id, band_num = band_tuple
            raster_path = self.get_raster_path(band_tuple[0])
        else:
            print('Error: band_id not found: {}'.format(band_id))
            return None
        if raster_path is not None:
            return (raster_path, band_tuple[1])

    # Make name from a string using the templates
    def name(self, namestring):
        for key in self.namecodes.keys():
            namestring = namestring.replace(key, self.namecodes.get(key, ''))
        return namestring
