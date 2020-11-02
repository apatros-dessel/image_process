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

landsat_files = [
    'band_coastal', # The first file must have the basic resolution for the scene
    'band_blue',
    'band_green',
    'band_red',
    'band_nir',
    'band_swir1',
    'band_swir2',
    'band_pan',
    'band_cirrus',
    'band_tirs1',
    'band_tirs2',
    'band_qa'
]

landsat_bandpaths = OrderedDict(
    {
            'coastal':  ('band_coastal',  1),
            'blue':     ('band_blue',     1),
            'green':    ('band_green',    1),
            'red':      ('band_red',      1),
            'nir':      ('band_nir',      1),
            'swir1':    ('band_swir1',    1),
            'swir2':    ('band_swir2',    1),
            'pan':      ('band_pan',      1),
            'cirrus':   ('band_cirrus',   1),
            'tirs1':    ('band_tirs1',    1),
            'tirs2':    ('band_tirs2',    1),
            'quality':  ('band_qa',       1)

        }
)


# landsat_names = OrderedDict(
#     {
#         'metadata':  r'<ls8_id>_MTD',
#         'angels':    r'<ls8_id>_ANG',
#     }
# )

# landsat_bandpaths = {
#     'LS8': {'coastal': '1', 'blue': '2', 'green': '3', 'red': '4', 'nir': '5', 'swir1': '6', 'swir2': '7', 'pan': '8', 'cirrus': '9', 'tirs1': '10', 'tirs2': '11', 'quality': 'QUALITY', 'qa': 'QUALITY'}
# }



# def get_from_text(pathfile, text):
#     with open(pathfile) as f:
#         for line in f:
#             if text in line:
#                 value = line.split("= ", 1)[1]
#     return value

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
def get_meta_landsat(mtl_list, call):
    #mtl_list = mtl2list(path)
    val = ''
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


def get_files_landsat(text, word):
    list_names = []
    for i in range(1, 12):
        list_names.append(get_meta_landsat(text, word+str(i)))
    list_names.append(get_meta_landsat(text, word+'QUALITY'))
    return list_names

def getlandsatfiles(text):
    file_list = get_files_landsat(text, "FILE_NAME_BAND_")
    # scroll(file_list)
    file_dict = OrderedDict()
    for file in file_list:
        if 'B1' in file and 'B10' not in file and 'B11' not in file:
            file_dict[landsat_files[0]] = file
        elif 'B2' in file:
            file_dict[landsat_files[1]] = file
        elif 'B3' in file:
            file_dict[landsat_files[2]] = file
        elif 'B4' in file:
            file_dict[landsat_files[3]] = file_list[3]
        elif 'B5' in file:
            file_dict[landsat_files[4]] = file_list[4]
        elif 'B6' in file:
            file_dict[landsat_files[5]] = file_list[5]
        elif 'B7' in file:
            file_dict[landsat_files[6]] = file_list[6]
        elif 'B8' in file:
            file_dict[landsat_files[7]] = file_list[7]
        elif 'B9' in file:
            file_dict[landsat_files[8]] = file_list[8]
        elif 'B10' in file:
            file_dict[landsat_files[9]] = file_list[9]
        elif 'B11' in file:
            file_dict[landsat_files[10]] = file_list[10]
        elif 'BQA' in file:
            file_dict[landsat_files[11]] = file_list[11]

    # for file in file_list:
    #     if 'Analytic' or 'MS' in file:
    #         file_dict['Analytic'] = file_list.pop(file_list.index(file)).replace('/execdir/', '')
    #         break

    return file_dict

def getlandsatdatetime(aq_date_time): #FILE_DATE = 2019-05-20T19:05:31Z
    year, month, day = intlist(aq_date_time[:10].split('-'))
    hour, minute, second = intlist(aq_date_time[11:19].split(':'))
    dtime = datetime(year, month, day, hour, minute, second)
    return dtime

# Fill <landsat_name> metadata
def metadata(path):

    meta = scene_metadata('LST')
    meta.container['text'] = landsat_data = mtl2list(path) # some code to get all metadata

    meta.sat = get_meta_landsat(landsat_data, "SPACECRAFT_ID")         # get satellite id as str
    meta.fullsat = 'LS8{}'.format(meta.sat)     # get satellite fullid as str
    meta.id = get_meta_landsat(landsat_data, "LANDSAT_PRODUCT_ID")           # get scene id as str
    meta.lvl = meta.id[5:7]

    meta.mtl = mtl2orderdict(path)
    meta.files = globals()['landsat_files'] # get files_id list


    #meta.filepaths = slice_orderdict(meta.mtl, 'FILE_NAME_BAND_', delete_call=True) #номер бенда
    meta.filepaths = getlandsatfiles(landsat_data) #имя бенда

    # cur_meta = meta.container.get('text')
    # if cur_meta is None:
    #     print('Metadata file not found for {}'.format(meta.id))
    # else:
    #     meta.filepaths = {meta.files[0]: get_from_text(cur_meta, '???')} # get filepaths as OrderedDict
    #meta.filepaths =  make_paths(landsat_data, "FILE_NAME_BAND_")  # get filepaths as OrderedDict


    meta.bandpaths = globals()['landsat_bandpaths'] # get bandpaths as tuple of files_id and band numbers
    meta.location = meta.id[10:16]   # get scene location id
    meta.datetime = getlandsatdatetime(get_meta_landsat(landsat_data, "FILE_DATE"))    # get image datetime as datetime.datetime

    meta.namecodes.update(
        {
            '[sat]':        meta.sat,
            '[lvl]':        meta.lvl,
            '[fullsat]':    meta.fullsat,
            '[id]':         meta.id,
            '[location]':   meta.location,
        }
    )

    meta.write_time_codes(meta.datetime)

    # Optional:
    # meta.datamsk =        # path to vector data
    # meta.cloudmask =      # path to vector data

    return meta



# Landsat-8 metadata
# class landsat_8:
#
#     def __init__(self, path):
#         folder, file = os.path.split(path)
#         if check_name(file, globals()['filepattern']['LS8']):
#             self.files = globals()['bands']['LS8']
#             self.bands = globals()['bands']['LS8']
#             self.mtl = mtl2orderdict(path)
#             self.filenames = slice_orderdict(self.mtl, 'FILE_NAME_BAND_', delete_call = True)
#             self.bandpaths = list_orderdict([self.filenames, fill_orderdict(self.filenames, 1)])
#             year, month, day = intlist(self.mtl.get('DATE_ACQUIRED').split('-'))
#             self.date = dtime.date(year, month, day)
#             self.place = file[10:16]
#         else:
#             print('Wrong file name: {}'.format(file))

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    # print(feat)
    if meta is not None:
        metadata = meta.container.get('text')
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('datetime', get_meta_landsat(metadata, "FILE_DATE"))
        feat.SetField('clouds', float(get_meta_landsat(metadata, 'CLOUD_COVER ')))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sun_elev', get_meta_landsat(metadata, 'SUN_ELEVATION'))
        feat.SetField('sun_azim', get_meta_landsat(metadata, 'SUN_AZIMUTH '))
        feat.SetField('channels', 11)
        feat.SetField('format', '16U')
        feat.SetField('u_size', 'meter')
        feat.SetField('level', meta.name('[lvl]'))
        feat.SetField('sat_view', get_meta_landsat(metadata, 'ROLL_ANGLE'))

        feat.SetField('type', 'MS')
        feat.SetField('sat_azim', None)
        feat.SetField('rows', get_meta_landsat(metadata, 'REFLECTIVE_LINES'))
        feat.SetField('cols', get_meta_landsat(metadata, 'REFLECTIVE_SAMPLES'))
        feat.SetField('epsg_dat', int('326' + get_meta_landsat(metadata, 'UTM_ZONE')))

        feat.SetField('x_size', )
        feat.SetField('y_size', )
        feat.SetField('area', None)
    return feat










