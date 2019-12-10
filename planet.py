# Functions for processing landsat data

import os
import sys # to allow GDAL to throw Python Exceptions
try:
    from osgeo import gdal, ogr, osr
except:
    import gdal
    import ogr
    import osr
import math
import numpy as np
from collections import OrderedDict
import re
import xml.etree.ElementTree as et
import datetime as dtime

from limb import check_name, intlist, slice_orderdict

# Examples of Planet metadata filenames
# r'2376743_4865309_2019-05-20_0f2a_BGRN_Analytic_metadata.xml'
# r'20190910_081115_0e26_3B_AnalyticMS_metadata.xml'

filepattern = {
    'PLN': r'\d+_\d+_\S+_Analytic\S*_metadata.xml',
}

bands = {
    'PLN': {
        'blue': '1',
        'green': '2',
        'red': '3',
        'nir': '4'
    }
}

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
    return sing2sing(result, sing_to_sing, digit_to_float)

# Gets Planet file names as ordered dictionary
def getplanetfiles(xml_tree):
    file_list = get_from_tree(xml_tree, 'fileName')
    file_dict = OrderedDict()
    for file in file_list:
        if 'DN' in file:
            file_dict['mask'] = file_list.pop(file_list.index(file))
            break
    for file in file_list:
        if 'Analytic' or 'MS' in file:
            file_dict['Analytic'] = file_list.pop(file_list.index(file))
            break

    return file_dict

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

satlib = {
    'PLN': planet,
}








