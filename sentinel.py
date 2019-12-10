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

from tools import *

filepattern = {
    'SN2': r'MTD_MSIL\d[CA]\.xml',
}

bands = {
    'SN2': {'coastal_aerosol': '1', 'blue': '2', 'green': '3', 'red': '4', 'vegetation red edge 1': '5', 'vegetation red edge 2': '6', 'vegetation red edge 3': '7', 'nir': '8', 'narrow nir': '8b', 'water vapour': '9', 'swir - cirrus': '10', 'swir1': '11', 'swir2': '12'}
}

# Reads Landsat MTL file and returns metadata as element tree
def meta_sentinel(path, mtd = False):
    if mtd:
        path = os.path.split(path)[0] + r'\GRANULE'
        folder_mtd = os.listdir(path)[0]
        path = path + '\\' + folder_mtd + r'\MTD_TL.xml'
    try:
        return et.parse(path)
    except:
        raise Exception(('Cannot open file: ' + path))

def sentinel_filenames(source):
    file_names_dict = OrderedDict()
    root = source.getroot()  # source should be tree (made by "meta_sentinel" function)
    for obj in root.iter('IMAGE_FILE'):
        file_name = obj.text
        if file_name.endswith('m'):
            file_id = file_name[-7:]  # [-7:-4]
        else:
            file_id = file_name[-3:]
        if file_id.startswith('B'):
            file_id = file_id[1:]
            if file_id.startswith['0']:
                file_id = file_id[1:]
        file_names_dict[file_id] = '{}.jp2'.format(file_name)
    return file_names_dict



# Landsat-8 metadata
class sentinel_2:

    def __init__(self, path):
        folder, file = os.path.split(path)
        if check_name(file, globals()['filepattern']['SN2']):
            self.files = globals()['bands']['SN2'] # change according to different pixel sizes
            self.bands = globals()['bands']['SN2']
            self.msi = meta_sentinel(path)
            self.mtd = meta_sentinel(path, mtd=True)
            self.filenames = sentinel_filenames(self.msi)
            self.bandpaths = list_orderdict([self.filenames, fill_orderdict(self.filenames, 1)])
            year, month, day = intlist(self.meta_call('DATATAKE_SENSING_START')[:10].split('-'))
            self.date = dtime.date(year, month, day)
            self.place = file[10:16]
        else:
            print('Wrong file name: {}'.format(file))

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


satlib = {
    'SN2': sentinel_2,
}








