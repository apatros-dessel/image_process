# -*- coding: utf-8 -*-

# Auxilliary functions for image processor

import sys, os, re, shutil, xlrd, xlwt, csv
import numpy as np
import xml.etree.ElementTree as et
from collections import OrderedDict
from datetime import datetime
from copy import copy, deepcopy

default_temp = '{}\image_processor'.format(os.environ['TMP'])
silent = False

if not os.path.exists(default_temp):
    os.makedirs(default_temp)

# Class to make endless counter
class counter:
    def __init__(self, startfrom = 0, step = 1):
        self.count = startfrom - 1
        self.step = step
    def __iter__(self, startfrom = 0, step = 1):
        # self.restart(startfrom)
        self.step = step
        return self
    def __next__(self):
        self.count += self.step
        return self.count
    def next(self):
        return self.__next__()
    def restart(self, startfrom = 0):
        self.count = startfrom - 1
        return self

# An iterator endlessly returning None
class iternone:
    def __init__(self):
        pass
    def __iter__(self):
        return self
    def __next__(self):
        return None
    def next(self):
        return self.__next__()

# Check existance of file
def check_exist(path, ignore=False, check_size=None):
    if not ignore:
        if os.path.exists(path):
            if check_size:
                if os.path.getsize(path)<check_size:
                    return False
            return True
    return False

# Conversts non-list objects to a list of length 1
def obj2list(obj):
    new_obj = copy(obj)
    if isinstance(new_obj, (tuple, list)):
        return new_obj
    else:
        return [new_obj]

# Returns list values by order
def list_order(orig_list):

    sorted_list = copy(orig_list)
    sorted_list.sort()

    order_list = []
    prev_val = sorted_list[0]
    prev_id = orig_list.index(prev_val)
    order_list.append(prev_id)
    copy_list = copy(orig_list)
    repeat_num = 0

    for val in sorted_list[1:]:

        id = orig_list.index(val)

        if id==prev_id:
            copy_list.pop(id)
            repeat_num += 1
            prev_id = copy_list.index(val) + repeat_num
            order_list.append(prev_id)
        else:
            order_list.append(id)
            prev_id = id
            copy_list = copy(orig_list)
            repeat_num = 0

    return order_list

# Sort list of lists (of the same length): the previous lists have higher priority
def sort_multilist(list_of_lists):

    def order_for_val(list_of_lists, match_value, level=0, reposition=None):
        match_list = []
        for i, val in enumerate(list_of_lists[level]):
            if match_value == val:
                match_list.append(i)
        if len(match_list) == 0:
            return 0, None
        elif len(match_list) == 1:
            return 1, match_list[0]
        elif len(list_of_lists) == 1:
            if reposition is not None:
                export_list = []
                for val in match_list:
                    export_list.append(reposition[val])
            else:
                export_list = match_list
            return 2, export_list
        else:
            next_level_list = []
            for old_list in list_of_lists[1:]:
                new_list = []
                for id in match_list:
                    new_list.append(old_list[id])
                next_level_list.append(new_list)
            return 2, order_for_level(next_level_list, reposition=match_list)

    def order_for_level(list_of_lists, reposition=None):
        count = 0
        export_order_list = []
        order_list = list_order(list_of_lists[0])
        for id, pos in enumerate(order_list):
            if id < count:
                continue
            else:
                res, value = order_for_val(list_of_lists, list_of_lists[0][pos], reposition=reposition)
                if res == 0:
                    continue
                elif res == 1:
                    if reposition is not None:
                        value = reposition[value]
                    export_order_list.append(value)
                    count += 1
                elif res == 2:
                    for val in value:
                        export_order_list.append(val)
                    count += len(value)
                else:
                    print('Unknown res: {}'.format(res))
                    raise Exception()
        return export_order_list

    return order_for_level(list_of_lists)

def order_for_val(list_of_lists, match_value, level=0):
    match_list = []
    for i, val in enumerate(match_list[level]):
        if match_value == val:
            match_list.append(i)
    if len(match_list) == 0:
        return 0, None
    elif len(match_list) == 1:
        return 1, [match_list[0]]
    else:
        next_level_list = []
        for old_list in list_of_lists[1:]:
            new_list = []
            for id in match_list:
                new_list.append(match_list[id])
            next_level_list.append(new_list)
        return 2, order_for_level(next_level_list)

def order_for_level(list_of_lists):
    count = 0
    export_order_list = []
    order_list = list_order(list_of_lists[0])
    for id, pos in enumerate(order_list):
        if id < count:
            continue
        else:
            res, value = order_for_val(list_of_lists, list_of_lists[pos])
            if res == 0:
                continue
            elif res == 1:
                order_list.extend(value)
                count += 1
            elif res == 2:
                order_list.extend(value)
                count += len(value)
            else:
                print('Unknown res: {}'.format(res))
                raise Exception()

# Unite all lists in a list of lists into a new list
def unite_multilist(list_of_lists):
    if len(list_of_lists) == 0:
        return []
    full_list = copy(list_of_lists[0])
    for list_ in list_of_lists[1:]:
        if isinstance(list_, list):
            full_list.extend(list_)
        else:
            print('Error: object is not a list: {}'.format(list_))
    return full_list

# Repeats th last value in the list until it has the predefined length
def list_of_len(list_, len_):
    while len(list_) < len:
        list_.append(list_[-1])
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

# Remove value from list
def RemoveFromList(list_, val_):
    report = []
    if val_ in list_:
        for val in list_:
            if val!=val:
                report.append(val)


# Change all values in list using the function
def flist(l, func, copy=True):
    if copy:
        l = list(deepcopy(l))
    for i, v in enumerate(l):
        l[i] = func(v)
    return l

# Return mean
def mean(x):
    y = 0
    for i in x:
        y += i
    return y/len(x)

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

# Splits path to folder, name and extension
def split3(path):
    if os.path.isdir(path):
        return path, '', ''
    folder, file = os.path.split(path)
    name, ext = os.path.splitext(file)
    return folder, name, ext[1:]

# Creates new name to avoid same names as in the list
def newname2(name, name_list, update_list=False):

    i = 2
    newname = '{}_{}'.format(name, i)
    while newname in name_list:
        newname = '{}_{}'.format(name, i)
        i += 1

    if update_list:
        name_list.append(newname)
        return newname, name_list
    else:
        return newname

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

# Creates new OrderedDict wuth keys from list
def endict(list_, obj = None, func = None):

    newordict = OrderedDict()

    if hasattr(func, '__callable__'):
        func = None

    if func is None:
        for key in list_:
            newordict[key] = deepcopy(obj)
    else:
        for key in dict:
            newordict[key] = func(key)

    return newordict

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

# Copy directory and all files in it
def copydir(path_in, dir_out):
    dir_in, folder_name = os.path.split(path_in)
    folders, files = folder_paths(path_in)
    for folder in folders:
        suredir(fullpath(dir_out, folder[len(dir_in):]))
    for file in files:
        shutil.copyfile(file, fullpath(dir_out, file[len(dir_in):]))

# Completely destroys dir with all contained files and folders
def destroydir(path, preserve_path = False):
    folders, files = folder_paths(path)
    success = []
    errors = []
    for file in files:
        try:
            os.remove(file)
            success.append(file)
        except:
            # os.remove(file)
            errors.append(file)
    folders.reverse()
    if preserve_path:
        folders = folders[:-1]
    for folder in folders:
        try:
            os.rmdir(folder)
            success.append(folder)
        except:
            errors.append(folder)
    if bool(errors):
        return False
    return True

# Check correctness of file name
def check_name(name, pattern):
    search = re.search(pattern, name)
    if search is None:
        return False
    else:
        return True

# Returns a list of two lists: 0) all folders in the 'path' directory, 1) all files in it
def fold_finder(path, filter_folder=[]):
    fold_ = []
    file_ = []
    # if len(path) >= 255:
        # return [[], []]
    try:
        dir_ = os.listdir(path)
        for name in dir_:
            if name in filter_folder:
                continue
            full = path + '\\' + name
            if os.path.isfile(full):
                file_.append(full)
            else:
                fold_.append(full)
    except:
        # print('Error fold_finder: %s' % path)
        pass
    return [fold_, file_]

# Searches filenames according to template and returns a list of full paths to them
# Doesn't use os.walk to avoid using generators
def walk_find(path, ids_list, templates_list, id_max=100000):
    #templates_list = listoftype(templates_list, str, export_tuple=True)
    ids_list = list(ids_list)
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
                    for template in templates:
                        if check_name(file_n, template):
                            export_.append((file_n, ids_list[i]))
        id += 1
    if len(path_list) > id_max:
        raise Exception('Number of folder exceeds maximum = {}'.format(id_max))
    return export_

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
    def create(self, file_extension = None):
        path_new = newdir(self.corner)
        if path_new is not None:
            self.paths.append(path_new)
            if file_extension is not None:
                path_new = newname(path_new, file_extension)
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
                print('DELETED: %s' % self.paths[i])
                self.paths.pop(i)
                return True
            else:
                print('ERROR: %s' % self.paths[i])
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
    # def __del__(self):
        # try:
            # destroydir(self.corner)
            # if self.empty() and cleardir(self.corner):
                # os.rmdir(self.corner)
        # except:
            # pass

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

def scroll(obj, print_type=True, decoding=None, header=None, lower=None, depth=0):
    tab = '  '*depth
    if header is not None:
        print(header)
    elif print_type:
        print('{}Object of {}:'.format(tab, type(obj)))
    if hasattr(obj, '__iter__') and not isinstance(obj, str):
        try:
            len_ = len(obj)
        except:
            len_ = 0
        if len_==0:
            print('{}<empty>'.format(tab+'  '))
        elif isinstance(obj, (dict, OrderedDict)):
            for val in obj:
                winprint('{}{}: {}'.format(tab+'  ', val, obj[val]), decoding=decoding)
        else:
            for val in obj:
                winprint('{}{}'.format(tab+'  ',val), decoding=decoding)
    else:
        winprint('{}{}'.format(tab+'  ',obj), decoding=decoding)
    if lower is not None:
        print(lower)

# Get datetime from string
def get_date_from_string(date_str):
    year = int(date_str[:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])
    hour = int(date_str[11:13])
    minute = int(date_str[14:16])
    second = float(re.search(r'\d+\.\d+', date_str[17:-1]).group())
    return datetime(year, month, day)

# Datetime object from string datetime as YYYY-MM-DDThh:mm:ss
def isodatetime(isodatestr):
    get = re.search('\d+-\d+-\d+T\d+:\d+:\d{2}', isodatestr)
    if get:
        date, time = get.group()[:-1].split('T')
        year, month, day = flist(date.split('-'), int)
        hour, minute, second = flist(time.split(':'), int)
        return datetime(year, month, day, hour, minute, second)

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
        data = ['text', 'tag', 'attrib'][data] or 'text'
    return_list = []
    if data == 'attrib':
        if attrib is None:
            for monodict in iter_list:
                return_list.append(mdval(monodict)['attrib'])
        else:
            for monodict in iter_list:
                attr_val = mdval(monodict)['attrib'].get(str(attrib))
                if attr_val is not None:
                    return_list.append(attr_val)
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
            if digit_to_float and obj.isdigit():
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
    return sing2sing(result, sing_to_sing, digit_to_float)

# Import data from xls
def xls_to_dict(path2xls, sheetnum=0):
    if path2xls:
        if os.path.exists(path2xls):
            rb = xlrd.open_workbook(path2xls)
            sheet = rb.sheet_by_index(sheetnum)
            keys = sheet.row_values(0)
            if len(keys)>1:
                keys = keys[1:]
                xls_dict = OrderedDict()
                for rownum in range(1, sheet.nrows):
                    rowdata = OrderedDict()
                    row = sheet.row_values(rownum)
                    for key, val in zip(keys, row[1:]):
                        rowdata[key] = val
                    xls_dict[row[0]] = rowdata
                return xls_dict
            else:
                print('Empty xls: %s' % path2xls)
                return None
    print('PATH NOT FOUND: %s' % path2xls)
    return None


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

# Scene metadata
class scene_metadata:

    def __init__(self, imsys):
        self.imsys = imsys       # Image system (Landsat, Sentinel, etc.) as str of length 3

        self.container = {}                     # Place to keep source metadata as a dictionary. Filled by the imsys-specific function

        self.sat = None                         # Satellite id (Landsat-8, Sentinel-2A, 0e26 (Planet id), etc.) as str
        self.fullsat = None                     # Fullname for identifying both satellite and imsys
        self.id = None,                         # A unique scene identifier
        self.lvl = None,                        # Data processing level
        self.files = OrderedDict()              # Dictionary of file ids
        self.filepaths = OrderedDict()          # Dictionary of filepaths
        self.bands = OrderedDict()              # Dictionary of bands
        self.bandpaths = OrderedDict()          # Dictionary of paths to bands (each path is a tuple of file id as str and band number as int)
        self.location = None                    # Scene location id
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
            'fullsat':      self.fullsat is not None,
            'id':           isinstance(self.id, str),
            'lvl':          self.lvl is not None,
            'files':        len(self.files) > 0,
            'filepaths':    len(self.filepaths) > 0,
            #'bands':       len(self.bands) > 0,
            'bandpaths':    len(self.bandpaths) > 0,
            'location':     self.location is not None,
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
            namestring = namestring.replace(key, delist(self.namecodes.get(key, '')))
        return namestring

# Searches filenames according to template and returns a list of full paths to them
def folder_paths(path, files = False, extension = None, id_max=100000, filter_folder=[]):
    # templates_list = listoftype(templates_list, str, export_tuple=True)
    if os.path.exists(path):
        if not os.path.isdir(path):
            path = os.path.split(path)[0]
        path_list = [path]
        path_list = [path_list]
    else:
        print('Path does not exist: {}'.format(path))
        return None
    id = 0
    export_files = []
    while id < len(path_list) < id_max:
        for id_fold, folder in enumerate(path_list[id]):
            fold_, file_ = fold_finder(folder, filter_folder=filter_folder)
            if fold_ != []:
                path_list.append(fold_)
            if extension is None:
                export_files.extend(file_)
            else:
                for f in file_:
                    if f.lower().endswith('.{}'.format(extension.lower())):
                        export_files.append(f)
        id += 1
    if len(path_list) > id_max:
        raise Exception('Number of folder exceeds maximum = {}'.format(id_max))
    if files:
        return export_files
    export_folders = unite_multilist(path_list)
    return export_folders, export_files

def count_dirsize(path):
    folders, files = folder_paths(path)
    byte_size = 0
    for file in files:
        byte_size += os.path.getsize(file)
    return byte_size

def str_size(byte_size):
    assert byte_size >= 0
    if byte_size < 1024:
        return u'{} байт'.format(round(byte_size, 2))
    elif byte_size < (1024**2):
        return u'{} Кб'.format(round(byte_size/1024, 2))
    elif byte_size < (1024**3):
        return u'{} Мб'.format(round(byte_size/(1024**2), 2))
    elif byte_size < (1024**4):
        return u'{} Гб'.format(round(byte_size/(1024**3), 2))
    elif byte_size < (1024**5):
        return u'{} Тб'.format(round(byte_size/(1024**4), 2))
    elif byte_size > (1024**6):
        print(u'Полученный размер больше 1 Пб, вероятно что-то пошло не так')
        return None

# destroydir(default_temp, preserve_path=True)

temp_dir_list = tdir()

# Make temp file or folder path with predefined extension
def tempname(ext = None):
    return globals()['temp_dir_list'].create(ext)

def colfromdict(dict_, key, listed=False):
    col_dict = OrderedDict()
    for linekey in dict_:
        col_dict[linekey] = dict_[linekey].get(key)
    if listed:
        return col_dict.values()
    return col_dict

def suredir(path, confirmed=True):
    if not os.path.exists(path):
        if confirmed:
            os.makedirs(path)
        elif Confirmation('Path does not exist: %s, create a new folder?' % path):
            os.makedirs(path)

def Confirmation(quest='y/n?'):
    while True:
        print(quest)
        try:
            confirm = str(input('  >>>  ')).lower()
            if confirm == 'y':
                return True
            elif confirm == 'n':
                return False
            else:
                print('Неверный код, введите "y" или "n"')
        except:
            print('Ошибка, введите "y" или "n"')

def delist(obj, item = 0):
    if isinstance(obj, (list, tuple)):
        return obj[item]
    else:
        return obj

# Returns data from txt file
def from_txt(txt, tmpt, format='s'):
    search = re.search(tmpt, txt)
    if search:
        data = search.group()
        if format=='s':
            return data
        elif format=='i':
            return int(data)
        elif format=='f':
            return float(data)

# Returns corner directory
def get_corner_dir(path, rank=1):
    if os.path.exists(path):
        path_ = path
        while rank:
            path_ = os.path.split(path_)[0]
            if path_==os.path.split(path_)[0]:
                break
            rank -= 1
        return path_

def find_parts(list_, start, fin):
    results = []
    passingby = True
    for i, line in enumerate(list_):
        if passingby:
            if re.search(start, line):
                i_start = i + 1
                passingby = False
        elif re.search(fin, line):
            results.append(list_[i_start:i])
            passingby = True
    return results

def dict_max_key(dict_):
    fin_key = None
    fin_val = None
    for key_ in dict_:
        if (fin_val is None):
            fin_key = key_
            fin_val = dict_[key_]
        elif dict_[key_]>fin_val:
            fin_key = key_
            fin_val = dict_[key_]
    return fin_key

def boolstr(val):
    if val:
        if val.lower() == 'false':
            val = False
        else:
            val = True
    return val

def liststr(str_, start='[', fin=']', spliter=',', toint=False, tofloat=False):
    if str_ is None:
        return None
    if start and str_.startswith(start):
        str_ = str_[len(start):]
    if fin and str_.startswith(fin):
        str_ = str_[:-len(fin)]
    result = str_.split(spliter)
    if tofloat:
        result = flist(result, float)
    elif toint:
        result = flist(result, int)
    return result

def dictstr(str_, start='{', fin='}', spliter=',', joiner=':', ordered=False, tofloat=False, toint=False):
    if str_ is None:
        return None
    if start and str_.startswith(start):
        str_ = str_[len(start):]
    if fin and str_.startswith(fin):
        str_ = str_[:-len(fin)]
    if ordered:
        result = OrderedDict()
    else:
        result = {}
    for keyval in str_.split(spliter):
        keyvallist = keyval.split(joiner)
        if len(keyvallist)!=2:
            print('Wrong dict input data: %s' % keyval)
            if len(keyvallist)<2:
                continue
        key, val = keyvallist[:2]
        if tofloat:
            result[float(key)] = float(val)
        elif toint:
            result[int(key)] = int(val)
        else:
            result[key] = val
    return result

def dict_to_csv(csv_path, csv_dict):
    with open(csv_path, 'w', newline='') as csvfile:
        dictwriter = csv.writer(csvfile, delimiter=';')
        for key in csv_dict:
            dictwriter.writerow([str(key), str(csv_dict[key])])

def delete(path):
    if os.path.exists(path):
        try:
            os.remove(path)
        except:
            print('CANNOT DELETE: %s' % path)

def Do(func, *args, **kwargs):
    if globals().get('_test', False):
        return func(*args, **kwargs)
    else:
        try:
            return func(*args, **kwargs)
        except:
            print('Do() ERROR')