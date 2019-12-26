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

templates = (
    r'LC08_L1TP_\d{6}_\d{8}_\d{8}_01_T1_MTL.txt',
)

bands = {
    'LS8': {'coastal': '1', 'blue': '2', 'green': '3', 'red': '4', 'nir': '5', 'swir1': '6', 'swir2': '7', 'pan': '8', 'cirrus': '9', 'tirs1': '10', 'tirs2': '11', 'quality': 'QUALITY', 'qa': 'QUALITY'}
}

# Returns MTL data as list
def mtl2list(path):
    mtl = open(path).read()
    mtl_list = re.split('  ', mtl)
    for i in range(len(mtl_list)):
        mtl_list[i] = mtl_list[i].strip()
    while '' in mtl_list:
        mtl_list.remove('')
    return mtl_list

# Makes an ordered dictionary of all
def mtl2orderdict(path):
    mtl_list = mtl2list(path)
    orderdict = OrderedDict()
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
            orderdict[key] = val
    return orderdict

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

satlib = {
    'LS8': landsat_8,
}








