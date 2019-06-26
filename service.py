
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

''' service '''

# returns a list of two lists: 0) all folders in the 'path' directory, 1) all files in it
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

# searches filenames according to template and returns a list of full paths to them
# doesn't use os.walk because of its unreckognized conflict with "process" class
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


# Returns call for re to find metadata file specified by the satellite and the sensor type
def input_call(image_id):
    input_call_list = {
      'Landsat': r"LC08_L1TP_\d{6}_\d{8}_\d{8}_\d\d_T1_?\d{,4}-?\d{,2}-?\d{,2}\b",
      'Sentinel': r"S2A_MSIL1C_\d{8}T\d{6}_N\d{4}_R\d{3}_.+.SAFE"
      }
    if image_id in input_call_list:
        return input_call_list[image_id]
    else:
        return None

# Splits path to folder and to file
def split_path(path):
    s = re.search(r'[^/\\]+\.[(txt)(xml)(jpg)(ip.tif)(tiff)(jp2)]+', path)
    if s is None:
        return path, ''
    else:
        file = s.group()
        folder = path[:len(path) - len(file) - 1]
        return folder, file

def list_fill(obj, length):
    obj_list = []
    for i in range(length):
        obj_list.append(obj)
    return obj_list

def par_undef(par_list, parname_list=None):
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

# Write data to raster (GeoTIFF)
def save_raster(path, param):
    band_array, proj, trans, dtype, noData = param
    xsize = len(band_array[1])
    ysize = len(band_array)
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    metadata = driver.GetMetadata
    if dtype is None:
        dtype = band_array.dtype
    dt = format_to_gdal(dtype)
    outData = driver.Create(path, xsize, ysize, 1, dt)
    outData.GetRasterBand(1).WriteArray(band_array)
    outData.GetRasterBand(1).SetNoDataValue(noData)
    outData.SetProjection(proj)
    outData.SetGeoTransform(trans)
    outData = None
    return

def format_to_gdal(dtype_in):
    format_dict = {'bool': 1, 'int': 3, 'float': 6, 'str': 2, np.bool: 1, \
      np.int16: 3, np.int32: 5, np.float32: 6, np.float64: 7}
    x = np.array([1])
    try:
        for key in format_dict:
            if dtype_in == x.astype(key).dtype:
                return format_dict[key]
    except:
        print(('Error reading formats: ' + str(dtype_in) + ', ' + str(key)))
    print(('Unknown format: ', str(dtype_in)))
    return gdal.GDT_Byte # If format unknown returns GDT_Float32

def sing2sing(obj, sing_to_sing=True, digit_to_float=True):
    try:
        obj = list(obj)
        for val_id in range(len(obj)):
            obj[val_id] = str(obj[val_id])
    except:
        raise Exception('Incorrect data type: list of strings is needed')
    if sing_to_sing:
        if len(obj) == 1:
            obj = obj[0]
            if digit_to_float:
                try:
                    obj = float(obj)
                except:
                    pass
    return obj

# Calculate NDVI
def ndvi(red, nir):
    nom = nir - red
    denom = red + nir
    ndvi = np.zeros(red.shape, dtype=red.dtype)
    ndvi[denom!=0] = nom[denom!=0] / denom[denom!=0]
    return ndvi

def TIF(path):
    if path.lower().endswith('.tiff') or path.lower().endswith('.tif'):
        return path
    else:
        return (path + '.tif')