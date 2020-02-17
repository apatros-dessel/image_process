# -*- coding: utf-8 -*-

# Functions for geodata processing

import os
try:
    from osgeo import gdal, ogr, osr
except:
    import gdal
    import ogr
    import osr
import numpy as np
import math

from tools import *

from raster_data import RasterData, MultiRasterData

from calc import array3dim, segmentator, limits_mask, data_to_image, get_raster_limits, band_by_limits

temp_dir_list = tdir(default_temp)

tiff_compress_list = [
    'JPEG',
    'LZW',
    'PACKBITS',
    'DEFLATE',
    'CCITTRLE',
    'CCITTFAX3',
    'CCITTFAX4',
    'LZMA',
    'ZSTD',
    'LERC',
    'LERC_DEFLATE',
    'LERC_ZSTD',
    'WEBP',
    'NONE'
]

ogr_dt_dict = {
    # int:              0,      # ogr.OFTInteger
    int:                1,      # ogr.OFTIntegerList
    float:              2,      # ogr.OFTReal
    #                   3,      # ogr.OFTRealList
    str:                4,      # ogr.OFTString
    #                   5,      # ogr.OFTStringList
    #                   6,      # ogr.OFTWideString
    #                   7,      # ogr.OFTWideStringList
    bool:               8,      # ogr.OFTBinary
    # datetime.date:    9,      # ogr.OFTDate
    # datetime.time:    10,     # ogr.OFTTime
    # datetime.datetime:11,     # ogr.OFTDateTime
    #                   12,     # ogr.OFTInteger64
    #                   13,     # ogr.OFTInteger64List
}

# Define ogr data type
def ogr_dt(dtype):
    return globals()['ogr_dt_dict'].get(type, 4)

# Creates GDAL Create or CreateCopy options list
def gdal_options(compress = None):

    options = []

    if compress is not None:
        if compress in globals()['tiff_compress_list']:
            options.append('COMPRESS={}'.format(compress))
        else:
            print('Unknown compression method: {}, use one of the following:'.format(compress))
            scroll(globals()['tiff_compress_list'], print_type=False)


    return options


# Checks raster arrays' number of dimensions and returns a list with a single array if it equals 2
def array3dim(raster_array):
    if raster_array.ndim == 2:
        raster_array = np.array([raster_array])
    elif raster_array.ndim != 3:
        raise Exception('Incorrect band_array shape: {}'.format(raster_array.shape))
    return raster_array

# Creates an ordered dictionary of forbidden column names
def forbid_names_dict(geom_col_name=None, lyr_defn_name=None, field_defn_col_name=None, orignames=[]):

    rep_names_dict = {}

    for name in [geom_col_name, lyr_defn_name, field_defn_col_name]:
        if name is not None:
            rep_names_dict[name] = newname2(name, orignames)

    if len(rep_names_dict) == 0:
        return None
    else:
        return rep_names_dict


# Converts data format to a proper gdal format index
def format_to_gdal(dtype_in):
    format_dict = {'bool': 1, 'int': 3, 'float': 6, 'str': 2, 'uint16': 3, np.bool: 1, np.int16: 3, np.int32: 5, np.float32: 6, np.float64: 7}
    x = np.array([1])
    try:
        for key in format_dict:
            if dtype_in == x.astype(key).dtype:
                return format_dict[key]
    except:
        print(('Error reading formats: ' + str(dtype_in) + ', ' + str(key)))
        print('Unknown format: {}'.format(dtype_in))
    return gdal.GDT_Byte

# Returns osr coordinate system from EPSG
def get_projection(proj_id=3857):
    t_crs = osr.SpatialReference()
    t_crs.ImportFromEPSG(int(proj_id))
    return t_crs

# Converts ogr dataset to a predefined projection
def vec_to_crs(ogr_dataset, t_crs, export_path):
    ogr_layer = ogr_dataset.GetLayer()
    v_crs = ogr_layer.GetSpatialRef()
    if v_crs.ExportToUSGS() != t_crs.ExportToUSGS():
        coordTrans = osr.CoordinateTransformation(v_crs, t_crs)
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(export_path): # the shapefile is created in the cwd
            driver.DeleteDataSource(export_path)
        outDataSet = driver.CreateDataSource(export_path)
        outLayer = outDataSet.CreateLayer("temp", geom_type=ogr.wkbMultiPolygon)
        outLayerDefn = outLayer.GetLayerDefn()
        feat = ogr_layer.GetNextFeature()
        while feat:
            geom = feat.GetGeometryRef()
            geom.Transform(coordTrans)
            out_feat = ogr.Feature(outLayerDefn)
            out_feat.SetGeometry(geom)
            for i in range(0, outLayerDefn.GetFieldCount()):
                out_feat.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
            outLayer.CreateFeature(out_feat)
            out_feat = None
            feat = ogr_layer.GetNextFeature()
    else:
        outDataSet = ogr_dataset
    return outDataSet

# Adapts the vector mask to the specified raster extent (the projections must be the same)
def extent_mask(array_shape, geotrans_0, extent):
    geotrans = list(geotrans_0)
    if isinstance(array_shape, (tuple, list)) == False:
        print('Wrong shape format: {}'.format(type(array_shape)))
        return array_shape, geotrans_0
    if geotrans[2] != 0 or geotrans[4] != 0:
        print('Inappropriate geotrans: {}, cannot apply mask'.format(geotrans))
        return array_shape, geotrans_0
    y_size, x_size = array_shape
    x_0 = geotrans[0]
    y_0 = geotrans[3]
    if math.fabs(geotrans[1]) == math.fabs(geotrans[5]):
        pix_size = math.fabs(geotrans[1])
    else:
        pix_size = (math.fabs(geotrans[1]) + math.fabs(geotrans[5])) / 2
        print('Pixels are not square, shape is: {}'.format([math.fabs(geotrans[1]), math.fabs(geotrans[5])]))
    x_min, x_max, y_min, y_max = extent
    x_lim = x_0 + x_size * pix_size
    if x_min <= x_0:
        if x_max <= x_0:
            print('Error: X extent out of range')
            return array_shape, geotrans_0
        else:
            x_min = x_0; x_lw_lim = 0
    else:
        x_lw_lim = int(math.floor((x_min - x_0) / pix_size))
        geotrans[0] = x_0 + x_lw_lim * pix_size
    if x_max > x_lim:
        x_max = x_lim; x_up_lim = x_size
    else:
        x_up_lim = int(math.ceil((x_max - x_0) / pix_size))
    y_lim = y_0 - y_size * pix_size
    if y_max >= y_0:
        if y_min >= y_0:
            print('Error: Y extent out of range')
            return array_shape, geotrans_0
        else:
            y_max = y_0; y_lw_lim = 0
    else:
        y_lw_lim = int(math.floor((y_0 - y_max) / pix_size))
        geotrans[3] = y_0 - y_lw_lim * pix_size
    if y_min < y_lim:
        y_min = y_lim; y_up_lim = y_size
    else:
        y_up_lim = int(math.ceil((y_0 - y_min) / pix_size))
    array_shape_new = (y_up_lim - y_lw_lim, x_up_lim - x_lw_lim)
    limits = (y_lw_lim, y_up_lim, x_lw_lim, x_up_lim)
    return array_shape_new, tuple(geotrans), limits

# Returns a mask as np.array of np.bool
def vector_mask(layer, array_shape, geotrans):
    y_res, x_res = array_shape
    target_ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform(geotrans)
    target_band = target_ds.GetRasterBand(1)
    target_band.SetNoDataValue(0)
    try:
        s = gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[1]) # This code raises warning if the leyer does not have a projection definition
    except:
        print('No pixels to filter in vector mask')
    mask = target_band.ReadAsArray().astype(bool)
    return mask

# Write data to raster (GeoTIFF)
def save_raster(path, band_array, copypath = None, proj = None, trans = None, dt = None, nodata = None, compress = None, overwrite = True):

    # print(np.unique(band_array))

    if check_exist(path, overwrite):
        return 1

    if copypath is not None:
        copy_ds = gdal.Open(copypath)
        if proj is None:
            proj = copy_ds.GetProjection()
        if trans is None:
            trans = copy_ds.GetGeoTransform()
        if nodata is None:
            nodata = copy_ds.GetRasterBand(1).GetNoDataValue()

    band_array = array3dim(band_array)

    if dt is None:
        dt = format_to_gdal(band_array.dtype)
    xsize = len(band_array[0][0])
    ysize = len(band_array[0])
    format = "GTiff"
    driver = gdal.GetDriverByName(format)

    options = gdal_options(compress=compress)

    outData = driver.Create(path, xsize, ysize, len(band_array), dt, options = options)

    for band_num in range(1, len(band_array)+1):
        outData.GetRasterBand(band_num).WriteArray(band_array[band_num-1])
        if nodata is not None:
            outData.GetRasterBand(band_num).SetNoDataValue(nodata)
    outData.SetProjection(proj)
    outData.SetGeoTransform(trans)
    outData = None

    return 0

def clip_raster(path2raster, path2vector, export_path = None, byfeatures = True, exclude = False, nodata = 0, path2newshp = None, compress = None, overwrite = True):
    raster_ds = gdal.Open(path2raster)
    vector_ds = ogr.Open(path2vector)
    crs_wkt = raster_ds.GetProjection()
    crs = osr.SpatialReference()
    crs.ImportFromWkt(crs_wkt)
    geotrans = list(raster_ds.GetGeoTransform())
    y_size = raster_ds.GetRasterBand(1).YSize;
    x_size = raster_ds.GetRasterBand(1).XSize
    raster_shape = (y_size, x_size)
    raster_array = []
    for band in list(range(1, raster_ds.RasterCount + 1)):
        raster_array.append(raster_ds.GetRasterBand(int(band)).ReadAsArray())
    raster_array = np.array(raster_array)
    if path2newshp is None:
        path2newshp = newname(temp_dir_list.create(), 'shp')
    outDataSet = vec_to_crs(vector_ds, crs, path2newshp)
    outLayer = outDataSet.GetLayer()
    extent = outLayer.GetExtent()
    t_shape, geotrans, limits = extent_mask(raster_shape, geotrans, extent)
    y_lw_lim, y_up_lim, x_lw_lim, x_up_lim = limits
    raster_array = raster_array[:, y_lw_lim: y_up_lim, x_lw_lim: x_up_lim]
    if byfeatures:
        mask_vector = vector_mask(outLayer, t_shape, geotrans)
        raster_array[:, mask_vector == exclude] = nodata
    param = raster_array, crs_wkt, tuple(geotrans), raster_array.dtype, nodata
    if export_path is None:
        export_path = newname(temp_dir_list.create(), 'tif')
    res = save_raster(export_path, raster_array, proj = crs_wkt, trans = tuple(geotrans), nodata = nodata, compress = compress, overwrite=overwrite)
    return res

# The code below has been take from 'merge_raster' plugin by S.Sadkov, I havent checked correspondence with other functions here
interpol_method = [gdal.GRA_NearestNeighbour, gdal.GRA_Average, gdal.GRA_Bilinear, gdal.GRA_Cubic, gdal.GRA_CubicSpline, gdal.GRA_Lanczos]

def ds(path = None, driver_name = 'GTiff', copypath = None, options = None, editable = False, overwrite=True):

    if path is None:
        path = ''
        driver_name = 'MEM'
    elif check_exist(path, ignore=overwrite):
        return None

    xsize = 1
    ysize = 1
    bandnum = 1
    dt = 0
    prj = ''
    geotrans = (0,1,0,0,0,1)
    nodata = 0

    if copypath is not None:
        copy_ds = gdal.Open(copypath)
        if copy_ds is not None:
            xsize = copy_ds.RasterXSize
            ysize = copy_ds.RasterYSize
            bandnum = copy_ds.RasterCount
            dt = copy_ds.GetRasterBand(1).DataType
            prj = copy_ds.GetProjection()
            geotrans = copy_ds.GetGeoTransform()
            nodata = copy_ds.GetRasterBand(1).GetNoDataValue()

    options = deepcopy(options)
    if options is not None:
        xsize = options.pop('xsize', xsize)
        ysize = options.pop('ysize', ysize)
        bandnum = options.pop('bandnum', bandnum)
        dt = options.pop('dt', dt)
        prj = options.pop('prj', prj)
        geotrans = options.pop('geotrans', geotrans)
        nodata = options.pop('nodata', nodata)

        if 'compress' in options:
            options = gdal_options(options.get('compress'))
        else:
            options = []
    else:
        options = []

    driver = gdal.GetDriverByName(driver_name)
    raster_ds = driver.Create(path, xsize, ysize, bandnum, dt, options = options)
    raster_ds.SetProjection(prj)
    raster_ds.SetGeoTransform(geotrans)

    if nodata is not None:
        raster_ds.GetRasterBand(1).SetNoDataValue(nodata)

    if editable and (driver_name != 'MEM'):
        raster_ds = None
        raster_ds = gdal.Open(path, 1)

    return raster_ds


# Create shapefile vector dataset
def shp(path2shp, editable = False):

    gdal.UseExceptions()

    if not os.path.exists(os.path.split(path2shp)[0]):
        os.makedirs(os.path.split(path2shp)[0])

    if path2shp.endswith('.shp'):
        dst_layername = path2shp[:-4]
    else:
        dst_layername = path2shp
        path2shp = path2shp + ".shp"

    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(path2shp)
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=None)

    if not editable:
        dst_ds = None

    return dst_ds

# Create GeoJSON vector dataset
def json(path2json, editable = False):

    gdal.UseExceptions()

    if not os.path.exists(os.path.split(path2json)[0]):
        os.makedirs(os.path.split(path2json)[0])

    if path2json.endswith('.json'):
        dst_layername = path2json[:-4]
    else:
        dst_layername = path2json
        path2shp = path2json + ".json"

    drv = ogr.GetDriverByName("GeoJSON")

    if os.path.exists(path2json):
        drv.DeleteDataSource(path2json)

    dst_ds = drv.CreateDataSource(path2json)
    dst_layer = dst_ds.CreateLayer('', srs=None)

    if not editable:
        dst_ds = None

    return dst_ds

def create_virtual_dataset(proj, geotrans, shape_, num_bands):
    y_res, x_res = shape_
    ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, num_bands, gdal.GDT_Byte)
    ds.SetGeoTransform(geotrans)
    ds.SetProjection(proj)
    return ds

def reproject_band(band, s_proj, s_trans, t_proj, t_trans, t_shape, dtype, method=gdal.GRA_Bilinear):
    y_size, x_size = band.shape
    driver = gdal.GetDriverByName('MEM')
    s_ds = driver.Create('', x_size, y_size, 0)
    s_ds.AddBand(dtype)
    s_ds.GetRasterBand(1).WriteArray(band)
    s_ds.SetGeoTransform(s_trans)
    s_ds.SetProjection(s_proj)
    t_ds = driver.Create('', t_shape[1], t_shape[0], 0)
    t_ds.AddBand(dtype)
    t_ds.SetGeoTransform(t_trans)
    t_ds.SetProjection(t_proj)
    gdal.ReprojectImage(s_ds, t_ds, None, None, method)
    return t_ds.ReadAsArray()

def band2raster(bandpath, t_raster, method, exclude_nodata = True, enforce_nodata = None, t_band_num = None, make_mask = False):

    s_raster_path, s_band_num = bandpath

    s_raster = gdal.Open(s_raster_path)
    s_proj = s_raster.GetProjection()
    s_trans = s_raster.GetGeoTransform()
    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    if s_band_num > s_raster.RasterCount:
        print('Band number exeeds RasterCount, the last band is taken')
        s_band_num = s_raster.RasterCount
    s_band_array = s_raster.GetRasterBand(s_band_num).ReadAsArray()
    dtype = s_raster.GetRasterBand(s_band_num).DataType
    if make_mask:
        mask_array = reproject_band((s_band_array != 0).astype(np.int8), s_proj, s_trans, t_proj, t_trans, t_shape, dtype, method).astype(bool)
    t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, dtype, method)
    if t_band_num is None:
        t_raster.AddBand(dtype)
        t_band_num = t_raster.RasterCount
    elif t_band_num > t_raster.RasterCount:
        t_band_num = t_raster.RasterCount
    if exclude_nodata:
        if enforce_nodata is None:
            enforce_nodata = s_raster.GetRasterBand(s_band_num).GetNoDataValue()
        if enforce_nodata is not None:
            t_raster.GetRasterBand(t_raster.RasterCount).SetNoDataValue(enforce_nodata)
    # t_raster.GetRasterBand(t_raster.RasterCount).WriteArray(t_band_array)
    t_raster.GetRasterBand(t_band_num).WriteArray(t_band_array)
    if make_mask:
        return mask_array
    else:
        return t_raster.RasterCount

def raster2raster(path2bands, path2export, path2target=None,  method = gdal.GRA_Bilinear, exclude_nodata = True, enforce_nodata = None, compress = None, overwrite = True):

    if check_exist(path2export, overwrite):
        return 1

    if path2target is None:
        path2target = path2bands[0][0]

    t_raster = gdal.Open(path2target)

    if t_raster is None:
        print('Cannot read dataset: {}'.format(path2target))
        return 1

    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    ds = create_virtual_dataset(t_proj, t_trans, t_shape, 0)

    for bandpath in path2bands:
        band2raster(bandpath, ds, method, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata)

    options = gdal_options(compress=compress)
    # scroll(options)

    driver = gdal.GetDriverByName('GTiff')
    outputData = driver.CreateCopy(path2export, ds, len(path2bands), options = options)
    outputData = None

    return 0

def get_band_array(path2band):
    path, bandnum = path2band
    ds = gdal.Open(path)
    if ds is None:
        print('Cannot open raster {}'.format(path))
        return None
    band = ds.GetRasterBand(bandnum)
    if band is None:
        print('Cannot get raster band from {}'.format(path2band))
        return None
    array = band.ReadAsArray()
    if array is None:
        print('Cannot get array from: {}'.format(path2band))
    return array

# Calculates difference between two bands
def band_difference(path2oldband, path2newband, export_path, nodata = 0, compress = None, overwrite = True):

    data_key = MultiRasterData((path2oldband, path2newband), data = [2,4])
    old_array, old_nodata = old = data_key.next()
    new_array, new_nodata = new = data_key.next()
    no_data_mask = np.zeros(old_array.shape).astype(bool)

    for arr, nodata_arr in (old, new):
        no_data_mask[arr==nodata_arr] = True
        arr = arr.astype(float)

    print(no_data_mask.shape)

    if (old_array is not None) and (new_array is not None):
        band_fin = (new_array - old_array).reshape(tuple([1] + list(new_array.shape)))
        print(band_fin.shape)
        band_fin[0][no_data_mask] = nodata
        res = save_raster(export_path, band_fin, copypath = path2newband[0], dt = 6, nodata = nodata, compress = compress, overwrite=overwrite)
    else:
        res = 1
    return res

# Calculates quotient between two bands
def band_quot(path2oldband, path2newband, export_path, nodata = 0, compress = None, overwrite = True):
    old_array = get_band_array(path2oldband).astype(float)
    new_array = get_band_array(path2newband).astype(float)
    if (old_array is not None) and (new_array is not None):
        band_fin = (new_array / old_array).reshape(tuple([1] + list(new_array.shape)))
        res = save_raster(export_path, band_fin, copypath = path2newband[0], dt = 6, nodata = nodata, compress = compress, overwrite=overwrite)
    else:
        res = 1
    return res

# Calculates quotient between two bands
def Changes(old_bandpaths, new_bandpaths, export_path,
            calc_path = None, formula = 0, nodata = 0,
            lower_lims = None, upper_lims = None, check_all_values = False, upper_priority = True,
            compress = None, overwrite = True):

    formula_list = [
        'MINUS',            # 0     # new - old
        'DIVISION',         # 1     # new / old
        'PERCENT_CHANGE',   # 2     # ((new / old) - 1) * 100
    ]

    assert len(old_bandpaths) == len(new_bandpaths)

    segmentize = not ((lower_lims is None) and (upper_lims is None))

    if segmentize:
        calc_path = r'{}\calc.tif'.format(globals()['temp_dir_list'].create())
    elif calc_path is None:
        calc_path = r'{}\calc.tif'.format(globals()['temp_dir_list'].create())

    print(calc_path)

    calc_ds = ds(calc_path, copypath=new_bandpaths[0][0], options={'dt': 6}, editable=True)

    old_bands = MultiRasterData(old_bandpaths, data = 2)
    new_bands = MultiRasterData(new_bandpaths, data = 2)

    for band_num, old_array, new_array in zip(counter(1), old_bands, new_bands):

        if formula == 0:
            band_fin = (new_array - old_array)
        elif formula == 1:
            band_fin = (new_array / old_array)
        elif formula == 2:
            band_fin = (((new_array / old_array) - 1) * 100)

        print(band_fin.shape)

        calc_ds.GetRasterBand(band_num).WriteArray(band_fin)

    calc_ds = None

    if segmentize:

        change_ds = ds(export_path, copypath=new_bandpaths[0][0], options={'dt': 1, 'bandnum': 1}, editable=True)
        change_set = RasterData(calc_path, data = 2)
        change_array = band_by_limits(change_set, upper_lims=upper_lims, lower_lims=lower_lims,
                                      check_all_values=check_all_values, upper_priority = upper_priority)
        change_ds.GetRasterBand(1).WriteArray(change_array)
        change_ds = None

    return 0

# Division of two bands with calculating percent of change
def percent(path2raster, export_path, band1 = 1, band2 = 1, nodata = 0, compress = None, overwrite = True):
    raster_ds = gdal.Open(path2raster)
    if raster_ds is not None:
        band1_array = raster_ds.GetRasterBand(band1).ReadAsArray().astype(np.float32)
        band2_array = raster_ds.GetRasterBand(band2).ReadAsArray().astype(np.float32)
    band_fin = ((band2_array / band1_array) * 100).reshape(tuple([1] + list(band1_array.shape)))
    band_fin[band_fin != 0] = band_fin[band_fin != 0] - 100
    param = band_fin, raster_ds.GetProjection(), raster_ds.GetGeoTransform(), band_fin.dtype, nodata
    res = save_raster(export_path, band_fin, copypath = path2raster, nodata = nodata, compress = compress, overwrite=overwrite)
    return res

# Saves data from a band in Dataset to polygon shapefile
def save_to_shp(path2raster, path2shp, band_num = 1, dst_fieldname = None, classify_table = None, export_values = None, overwrite = True):

    # Create ogr vector dataset
    gdal.UseExceptions()
    if not os.path.exists(os.path.split(path2shp)[0]):
        os.makedirs(os.path.split(path2shp)[0])
    if path2shp.endswith('.shp'):
        dst_layername = path2shp[:-4]
    else:
        dst_layername = path2shp
        path2shp = path2shp + ".shp"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(path2shp)
    dst_layer = dst_ds.CreateLayer(dst_layername, srs = None)
    if dst_fieldname is None:
        dst_fieldname = 'DN'
    fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
    dst_layer.CreateField(fd)
    dst_field = 0

    # Polygonize raster data
    #print(path2raster)
    raster_ds = gdal.Open(path2raster)
    if classify_table is not None:
        band_array = segmentator(raster_ds.GetRasterBand(band_num).ReadAsArray(), classify_table)
        temp_ds = create_virtual_dataset(raster_ds.GetProjection(), raster_ds.GetGeoTransform(), band_array.shape, 1)
        temp_ds.GetRasterBand(1).WriteArray(band_array)
        data_band = temp_ds.GetRasterBand(1)
    else:
        data_band = raster_ds.GetRasterBand(1)
        band_array = data_band.ReadAsArray()
    if export_values is not None:
        mask_array = np.zeros(band_array.shape).astype(bool)
        for val in np.unique(band_array):
            if val in export_values:
                mask_array[band_array == val] = True
        mask_ds = create_virtual_dataset(raster_ds.GetProjection(), raster_ds.GetGeoTransform(), band_array.shape, 1)
        mask_ds.GetRasterBand(1).WriteArray(mask_array.astype(int))
        mask_band = mask_ds.GetRasterBand(1)
    else:
        mask_band = None
    gdal.Polygonize(data_band, mask_band, dst_layer, dst_field, [], callback = gdal.TermProgress_nocb)
    dst_ds = None

    # Write projection
    write_prj(dst_layername + '.prj', raster_ds.GetProjection())
    return None

# Returns data on raster projection and geotransform parameters
def getrastershape(raster_ds):
    crs = osr.SpatialReference()
    crs.ImportFromWkt(raster_ds.GetProjection())
    crs_export = crs.ExportToUSGS()
    geotrans_export = raster_ds.GetGeoTransform()
    return crs_export, geotrans_export

# Returns raster data as np.array
def getbandarrays(path2bands):
    assert isinstance(path2bands, (tuple, list)) and (len(path2bands) > 0)
    raster_list = []
    #(path2bands)
    for path2raster, band_num in path2bands:
        raster_ds = gdal.Open(path2raster)
        if raster_ds is None:
            print('ERROR: cannot open raster file: {}'.format(path2raster))
            return None
        else:
            raster_list.append(raster_ds)
    baseshape = getrastershape(raster_list[0])
    for raster_ds in raster_list[1:]:
        if (getrastershape(raster_ds) != baseshape):
            path2start = []
            band_nums = []
            for path2raster, band_num in path2bands:
                path2start.append(path2raster)
                band_nums.append(band_num)
            path2export = newname(tdir().create(), 'tif')
            raster2raster(path2start, path2bands[0][0], path2export, band_nums = band_nums, method = gdal.GRA_Bilinear, exclude_nodata = True, enforce_nodata = None)
            return array3dim(gdal.Open(path2export).ReadAsArray())
    stack_list = []
    for i in range(len(raster_list)):
        stack_list.append(array3dim(raster_list[i].GetRasterBand(path2bands[i][1]).ReadAsArray()))
    return np.vstack(tuple(stack_list))

# Calculates normalized difference raster (for NDVI, NDWI and other indices calculation
def normalized_difference(path2bands, path2export, dt = None, compress = None, overwrite = True):
    data_array = getbandarrays(path2bands).astype(np.float)
    #print(data_array.shape)
    mask = np.ones(data_array.shape[1:]).astype(np.bool)
    for slice in data_array:
        mask[slice==0] = False
    nd_array = np.zeros(data_array.shape[1:])
    nd_array[mask] = (data_array[0][mask] - data_array[1][mask]) / (data_array[1][mask] + data_array[0][mask])
    res = save_raster(path2export, nd_array, copypath = path2bands[0][0], dt = dt, compress = compress, overwrite=overwrite)
    return res

index_calculator = {
    'Normalized': normalized_difference,
}

def write_prj(path2prj, projection):
    prj_handle = open(path2prj, 'w')
    prj_handle.write(projection)
    prj_handle.close()
    return None

# Unites all objects in a set of vector layers in a single layer
def unite_vector(path2vector_list, path2export): # No georeference check is used

    drv = ogr.GetDriverByName("ESRI Shapefile")
    t_ds = drv.CreateDataSource(path2export)
    t_lyr = t_ds.CreateLayer('Layer', srs = None)

    # Create attribute fields
    attr_list = []
    for i, path2vector in enumerate(path2vector_list):
        s_vector_ds = ogr.Open(path2vector)
        if s_vector_ds is None:
            print('Cannot open dataset: {}'.format(path2vector))
            continue
        s_lyr = s_vector_ds.GetLayer()
        for feat in s_lyr:
            feat_dict = OrderedDict()
            feat_attr_list = feat.keys()
            for attr_key in feat_attr_list:
                # print('{}: {}'.format(attr_key, feat.IsFieldNull(feat.GetFieldIndex(attr_key))))
                feat_dict[attr_key] = feat.GetField(attr_key)
                # print('{}: {} of {}'.format(attr_key, feat_dict[attr_key], type(feat_dict[attr_key])))
            attr_list.append(feat_dict)
            # scroll(feat_dict)
    attr_names_dict = OrderedDict()
    for dict_ in attr_list:
        for attr in dict_.keys():
            if attr not in attr_names_dict:
                attr_names_dict[attr] = type(dict_[attr])
                # print((type(dict_[attr])==str) + (type(dict_[attr])==int))

    scroll(attr_names_dict)
    for key in attr_names_dict:
        dtype = ogr_dt(attr_names_dict[key])
        field = ogr.FieldDefn(key, dtype)
        t_lyr.CreateField(field)

    # Create Features
    for i, path2vector in enumerate(path2vector_list):

        s_vector_ds = ogr.Open(path2vector)
        if s_vector_ds is None:
            print('Cannot open dataset: {}'.format(path2vector))
            continue
        s_lyr = s_vector_ds.GetLayer()

        for feat in s_lyr:
            # print(feat)
            t_lyr.CreateFeature(feat)
            newfeat = t_lyr.GetNextFeature()
            attr_list = feat.keys()
            # for attr_key in attr_names_dict:
                # attr_value = feat.GetField(attr_key)
                #print('  {}: {}'.format(attr_key, attr_value))
                # if attr_key not in attr_list:
                    # field = feat.GetFieldDefnRef(attr_key)
                    # print(field.GetName(), field.GetType())
                    # if field.GetType() == ogr.OFTString:
                        # print(field.GetWidth())
                        # pass
                    # t_lyr.CreateField(field)
                    # pass
            #print(newfeat.keys())

    t_ds = None

    write_prj(path2export[:-4] + '.prj', s_lyr.GetSpatialRef().ExportToWkt())

    return None

def vector_mask(path2raster, path2save_raster_mask, path2shp, limits, sign, nodata=None):

    raster_ds = gdal.Open(path2raster)

    if raster_ds is None:
        print('File not found: {}'.format(path2raster))
        return 1

    # Create mask as an array
    try:
        mask = limits_mask(raster_ds.ReadAsArray(), limits, sign)

    except MemoryError:
        print('Memory Error, try to process raster by bands')
        mask = np.zeros((raster_ds.RasterYSize, raster_ds.RasterXSize)).astype(np.bool)
        for band_num in range(1, raster_ds.RasterCount+1):
            mask_band = limits_mask(raster_ds.GetRasterBand(band_num), limits[band_num-1:band_num], sign)
            mask[mask_band] = True
            del(mask_band)

    # Create raster mask as dataset
    driver = gdal.GetDriverByName('GTiff')
    mask_ds = driver.Create(path2save_raster_mask, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Byte)
    mask_ds.SetProjection(raster_ds.GetProjection())
    mask_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    mask_ds = None
    mask_ds = gdal.Open(path2save_raster_mask, 1)
    mask_ds.GetRasterBand(1).WriteArray(mask)
    if nodata is not None:
        mask_ds.GetRasterBand(1).SetNoDataValue(nodata)
    mask_ds = None
    del(mask)

    save_to_shp(path2save_raster_mask, path2shp, export_values=[1])

    return None

def raster_to_image(path2raster, path2export, band_limits, gamma=1, exclude_nodata = True, enforce_nodata = None, compress=None):

    raster_ds = gdal.Open(path2raster)

    num_bands = min(raster_ds.RasterCount, len(band_limits))

    driver = gdal.GetDriverByName('GTiff')
    options = gdal_options(compress=compress)
    export_ds = driver.Create(path2export, raster_ds.RasterXSize, raster_ds.RasterYSize, num_bands, 1, options = options)
    export_ds.SetProjection(raster_ds.GetProjection())
    export_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    export_ds = None

    export_ds = gdal.Open(path2export, 1)

    for i in range(num_bands):
        band_num = i+1
        band_array = raster_ds.GetRasterBand(band_num).ReadAsArray()

        y_min = 1
        y_max = 255
        dy = 254
        x_min, x_max = band_limits[i][:2]
        dx = (x_max - x_min)
        band_array = band_array.astype(np.float)
        band_array = band_array - x_min
        # band_array = None
        band_array[band_array < 0] = 0
        band_array[band_array > dx ] = dx

        if gamma == 1:
            band_array = band_array * (dy/dx)
        else:
            band_array = band_array / dx
            band_array = band_array ** gamma
            band_array = band_array * dy

        band_array = band_array + y_min
        band_array[band_array < y_min] = y_min
        band_array[band_array > y_max] = y_max
        band_array = np.asarray(band_array)

        if exclude_nodata:
            nodata = raster_ds.GetRasterBand(band_num).GetNoDataValue()
            band_array[raster_ds.GetRasterBand(band_num).ReadAsArray()==nodata] = 0

            if enforce_nodata is not None:
                band_array[raster_ds.GetRasterBand(band_num).ReadAsArray()==enforce_nodata] = 0

            export_ds.GetRasterBand(band_num).SetNoDataValue(0)

        export_ds.GetRasterBand(band_num).WriteArray(band_array)

        band_array = None

    export_ds = None

    return None

def mosaic(import_list, path2export, prj, geotrans, xsize, ysize, band_num, dt, nptype=np.int8, method=gdal.GRA_CubicSpline, exclude_nodata=True, enforce_nodata=None, compress = None):

    driver = gdal.GetDriverByName('GTiff')
    options = gdal_options(compress=compress)
    temp_path = r'{}\{}'.format(os.path.split(path2export)[0], 'temp.tif')
    export_ds = driver.Create(temp_path, xsize, ysize, 1, dt, options=options)
    export_ds.SetProjection(prj)
    export_ds.SetGeoTransform(geotrans)
    export_ds = None

    fin_ds = driver.Create(path2export, xsize, ysize, band_num, dt, options=options)
    fin_ds.SetProjection(prj)
    fin_ds.SetGeoTransform(geotrans)
    fin_ds = None

    export_ds = gdal.Open(temp_path, 1)

    for band_id in range(1, band_num + 1):

        export_band = np.zeros((ysize, xsize)).astype(nptype)

        for path2raster in import_list:
            new_band_mask = band2raster((path2raster, band_id), export_ds, method=method, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata, t_band_num = 1, make_mask = True)
            new_band_data = export_ds.GetRasterBand(1).ReadAsArray()
            # print('new_band_data: {}'.format(np.unique(new_band_data, return_counts=True)))
            # new_band_mask = [new_band_data != 0]
            # print(np.mean(export_band))
            # print(np.mean(new_band_data))
            # print(np.mean(new_band_mask))
            export_band[new_band_mask] = new_band_data[new_band_mask]
            # print('export_band: {}'.format(np.unique('export_band: {}'.format(np.unique(new_band_data, return_counts=True)), return_counts=True)))
            new_band_data = None
            new_band_mask = None
            print('Done: {}'.format(os.path.basename(path2raster)))

        print('Export_band:\n {}'.format(np.unique(export_band, return_counts=True)))
        fin_ds = gdal.Open(path2export, 1)
        fin_ds.GetRasterBand(band_id).WriteArray(export_band)
        fin_ds = None
        export_band = None
        print('\nFinished export band %i\n' % band_id)

    export_ds = None

    return None

def alpha(path2raster, path2export, use_raster_nodata=True, use_limits_mask=False, lim_list=[(0)], sign='!=', band_mix = 'OR', options = None, overwrite = True):

    raster_data = RasterData(path2raster, data=1)

    if use_limits_mask:
        lim_list = list_of_len(lim_list, raster_data.len)
    else:
        lim_list = list_of_len([None], raster_data.len)

    mask = limits_mask(RasterData(path2raster), lim_list, sign=sign, band_mix=band_mix, include_raster_nodata=-use_raster_nodata)

    if mask is not None:
        raster_ds = ds(path=path2export, copypath=path2raster, options=options, editable=True, overwrite=overwrite)
        raster_ds.AddBand(1)
        raster_ds.GetRasterBand(raster_ds.RasterCount).WriteArray(mask*255)
        raster_ds = None
        return 0

    else:
        print('Error creating alpha channel')
        return 1

class bandpath:

    def __init__(self, filepath, bandnum, name = None):
        self.file = str(filepath)
        self.band = int(bandnum)
        self.name = name

    def getdataset(self):
        if os.path.exists(self.file):
            return gdal.Open(self.file)

    def getband(self):
        raster_ds = self.getdataset()
        if raster_ds is not None:
            if raster_ds.RasterCount >= self.band:
                return raster_ds.GetRasterBand(self.band)

    def __bool__(self):
        return self.getband() is not None

    def array(self):
        band = self.getband()
        if band is not None:
            return array3dim(band.ReadAsArray())

def RasterToImage(path2raster, path2export, method=0, band_limits=None, gamma=1, exclude_nodata = True, enforce_nodata = None, band_order = [1,2,3], compress = None, overwrite = True, alpha=False):

    if check_exist(path2export, ignore=overwrite):
        return 1

    options = {
        'dt': 1,
        'nodata': 0,
        'compress': compress,
        'bandnum': [3, 4][alpha],
    }

    t_ds = ds(path=path2export, copypath=path2raster, options=options, editable=True, overwrite=overwrite)

    source = RasterData(path2raster)

    error_count = 0
    band_num = 0

    if alpha:
        t_ds.GetRasterBand(4).WriteArray(np.full((source.ds.RasterYSize, source.ds.RasterXSize), 255))

    for band_id, raster_array, nodata in source.getting((0,2,3), band_order = band_order):

        res = 0

        band_num += 1

        if exclude_nodata and (nodata is not None):
            if enforce_nodata is not None:
                mask = (raster_array!=nodata) * (raster_array!=enforce_nodata)
            else:
                mask = raster_array!=nodata
        else:
            if enforce_nodata is not None:
                mask = raster_array!=enforce_nodata
            else:
                mask = None

        if np.min(mask) == True:
            mask = None

        if mask is not None:
            data = raster_array[mask]
        else:
            data = raster_array

        data = data_to_image(data, method=method, band_limits=band_limits, gamma=gamma)

        if data is None:
            print('Error calculating band %i' % band_id)
            error_count += 1
            continue

        if (mask is not None):
            raster_array[mask] = data
            raster_array[~ mask] = 0

        del data

        t_ds.GetRasterBand(band_num).WriteArray(raster_array)

        del raster_array

        if alpha and (mask is not None):
            oldmask = t_ds.GetRasterBand(4).ReadAsArray()
            oldmask[~ mask] = 0
            t_ds.GetRasterBand(4).WriteArray(oldmask)

        del mask

    if error_count == t_ds.RasterCount:
        res = 1

    t_ds = None

    return res

def RasterToImage2(path2raster, path2export, method=0, band_limits=None, gamma=1, exclude_nodata = True,
                   enforce_nodata = None, band_order = [1,2,3], compress = None, overwrite = True, alpha=False):

    if check_exist(path2export, ignore=overwrite):
        return 1

    options = {
        'dt': 1,
        'nodata': 0,
        'compress': compress,
        'bandnum': [3, 4][alpha],
    }

    t_ds = ds(path=path2export, copypath=path2raster, options=options, editable=True, overwrite=overwrite)

    source = RasterData(path2raster)

    error_count = 0
    band_num = 0

    if alpha:
        t_ds.GetRasterBand(4).WriteArray(np.full((source.ds.RasterYSize, source.ds.RasterXSize), 255))

    for band_id, raster_array, nodata in source.getting((0,2,3), band_order = band_order):

        res = 0

        band_num += 1

        if exclude_nodata and (nodata is not None):
            if enforce_nodata is not None:
                mask = (raster_array!=nodata) * (raster_array!=enforce_nodata)
            else:
                mask = raster_array!=nodata
        else:
            if enforce_nodata is not None:
                mask = raster_array!=enforce_nodata
            else:
                mask = None

        if np.min(mask) == True:
            mask = None

        if mask is not None:
            data = raster_array[mask]
        else:
            data = raster_array

        data = data_to_image(data, method=method, band_limits=band_limits[band_id-1], gamma=gamma)

        if data is None:
            print('Error calculating band %i' % band_id)
            error_count += 1
            continue

        if (mask is not None):
            raster_array[mask] = data
            raster_array[~ mask] = 0

        del data

        t_ds.GetRasterBand(band_num).WriteArray(raster_array)

        del raster_array

        if alpha and (mask is not None):
            oldmask = t_ds.GetRasterBand(4).ReadAsArray()
            oldmask[~ mask] = 0
            t_ds.GetRasterBand(4).WriteArray(oldmask)

        del mask

    if error_count == t_ds.RasterCount:
        res = 1

    t_ds = None

    return res

# RasterToImage with reprojection
def RasterToImage3(path2raster, path2export, method=0, band_limits=None, gamma=1, exclude_nodata = True,
                   enforce_nodata = None, band_order = [1,2,3], reprojectEPSG = None, reproject_method = gdal.GRA_Lanczos,
                   compress = None, overwrite = True, alpha=False):

    if check_exist(path2export, ignore=overwrite):
        return 1

    options = {
        'dt': 1,
        'nodata': 0,
        'compress': compress,
        'bandnum': [3, 4][alpha],
    }

    ds_in = gdal.Open(path2raster)
    if ds_in is None:
        print('Input raster not found: {}'.format(path2raster))
        return 1

    path2rgb = path2export
    reproject = False
    if reprojectEPSG is not None:
        reprojectEPSG = int(reprojectEPSG)
        srs_in = osr.SpatialReference()
        srs_in.ImportFromWkt(ds_in.GetProjection())
        srs_out = osr.SpatialReference()
        srs_out.ImportFromEPSG(reprojectEPSG)
        # print(srs_in.ExportToProj4(), srs_out.ExportToProj4())
        if srs_in.ExportToProj4() != srs_out.ExportToProj4():
            path2rgb = newname(globals()['temp_dir_list'].create(), 'tif')
            reproject = True


    t_ds = ds(path=path2rgb, copypath=path2raster, options=options, editable=True, overwrite=overwrite)

    error_count = 0
    band_num = 0

    source = RasterData(path2raster)

    if alpha:
        t_ds.GetRasterBand(4).WriteArray(np.full((source.ds.RasterYSize, source.ds.RasterXSize), 255))

    for band_id, raster_array, nodata in source.getting((0,2,3), band_order = band_order):

        res = 0

        band_num += 1

        if exclude_nodata and (nodata is not None):
            if enforce_nodata is not None:
                mask = (raster_array!=nodata) * (raster_array!=enforce_nodata)
            else:
                mask = raster_array!=nodata
        else:
            if enforce_nodata is not None:
                mask = raster_array!=enforce_nodata
            else:
                mask = None

        if np.min(mask) == True:
            mask = None

        if mask is not None:
            data = raster_array[mask]
        else:
            data = raster_array

        data = data_to_image(data, method=method, band_limits=band_limits[band_id-1], gamma=gamma)

        if data is None:
            print('Error calculating band %i' % band_id)
            error_count += 1
            continue

        if (mask is not None):
            raster_array[mask] = data
            raster_array[~ mask] = 0

        del data

        t_ds.GetRasterBand(band_num).WriteArray(raster_array)

        del raster_array

        if alpha and (mask is not None):
            oldmask = t_ds.GetRasterBand(4).ReadAsArray()
            oldmask[~ mask] = 0
            t_ds.GetRasterBand(4).WriteArray(oldmask)

        del mask

    if error_count == t_ds.RasterCount:
        res = 1

    t_ds = None

    if reproject:
        res = ReprojectRaster(path2rgb, path2export, reprojectEPSG, method = reproject_method, compress = compress, overwrite = overwrite)

    return res


# Reprojects Raster
def ReprojectRaster(path_in, path_out, epsg, method = gdal.GRA_Lanczos, compress = None, overwrite = True):

    if check_exist(path_out, ignore=overwrite):
        return 1

    ds_in = gdal.Open(path_in)

    if ds_in is None:
        print('File not found: {}'.format(path_in))
        return 1

    proj = ds_in.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    geotransform = ds_in.GetGeoTransform()
    x_res = geotransform[1]
    y_res = geotransform[5]
    # print(x_res, y_res)

    t_raster_base = gdal.AutoCreateWarpedVRT(ds_in, proj, srs.ExportToWkt())
    x_0, x, x_ang, y_0, y_ang, y =  t_raster_base.GetGeoTransform()
    newXcount = int(math.ceil(t_raster_base.RasterXSize * (x/x_res)))
    newYcount = int(math.ceil(t_raster_base.RasterYSize * (y/y_res)))

    options = {
        'dt':       ds_in.GetRasterBand(1).DataType,
        'prj':      t_raster_base.GetProjection(),
        'geotrans': (x_0, x_res, x_ang, y_0, y_ang, y_res),
        'bandnum':  ds_in.RasterCount,
        'xsize':    newXcount,
        'ysize':    newYcount,
        # 'nodata':   ds_in.GetNodataValue(),
        'compress': compress,
    }

    # scroll(options)
    ds_out = ds(path_out, options = options, editable = True)
    gdal.ReprojectImage(ds_in, ds_out, None, None, method)

    # print(t_raster_base.GetProjection())
    # print(ds_out.GetGeoTransform())

    ds_out = None

    return 0

def Mosaic(path2raster_list, export_path, band_num=1, options=None):

    # t_ds = gdal.BuildVRT(export_path, path2raster_list)

    tfolder = globals()['temp_dir_list'].create()
    tpath = newname(tfolder, 'tif')
    vrt = gdal.BuildVRT(tpath, path2raster_list)
    driver = gdal.GetDriverByName('GTiff')
    t_ds = driver.CreateCopy(export_path, vrt, band_num, options = options)
    t_ds = None

    print('Started mosaic of %i images' % len(path2raster_list))

    t_ds = gdal.Open(export_path, 1)
    for path2raster in path2raster_list:
        s_ds = gdal.Open(path2raster)
        gdal.ReprojectImage(s_ds, t_ds)
        print('Added to mosaic: {}'.format(path2raster))
        s_ds = None

    t_ds = None
    print('Finished mosaic of %i images' % len(path2raster_list))

    return 0

def RasterLimits(path2raster_list, method=0, band_limits=None, band_num = 3, exclude_nodata = True, enforce_nodata = None, mixing_method = 0):

    raster_bands_limits = []

    for path2raster in path2raster_list:

        raster_ds = gdal.Open(path2raster)

        if raster_ds is None:
            print('Cannot open raster: {}'.format(path2raster))
            continue

        raster_limits = []

        for i in range(band_num):

            if i > raster_ds.RasterCount:
                raster_limits.append(np.full((1,2), np.nan))

            raster_array = raster_ds.GetRasterBand(i+1).ReadAsArray()
            if exclude_nodata:
                raster_array = raster_array[raster_array != raster_ds.GetRasterBand(i+1).GetNoDataValue()]
            if enforce_nodata is not None:
                raster_array = raster_array[raster_array != enforce_nodata]

            min, max = get_raster_limits(raster_array, method=method, band_limits=band_limits)
            if min is None:
                min = np.nan
            if max is None:
                max = np.nan
            raster_limits.append(np.array([min, max]).reshape((1,2)))

        raster_bands_limits.append(np.hstack(raster_limits))

        print('Got raster limits: {}'.format(raster_limits))

        del raster_limits
        raster_ds = None

    raster_bands_limits = np.vstack(raster_bands_limits)

    print(raster_bands_limits)

    band_limits = []

    for i in range(band_num):

        min_col = raster_bands_limits[:,2*i]
        max_col = raster_bands_limits[:,2*i+1]

        if mixing_method == 0:
            min = np.min(min_col)
            max = np.max(max_col)

        elif mixing_method == 1:
            min = np.mean(min_col)
            max = np.mean(max_col)

        band_limits.append((min, max))

    return band_limits

# Saves raster data mask to shapefile
def RasterDataMask(path2raster, path2export, use_nodata = True, enforce_nodata = None, alpha=None, overwrite = True):

    if check_exist(path2export, ignore=overwrite):
        return 1

    s_ds = gdal.Open(path2raster)
    if s_ds is None:
        return 1

    tfolder = globals()['temp_dir_list'].create()
    tpath = newname(tfolder, 'tif')

    options = {
        'dt': 1,
        'nodata': 0,
        'compress': 'LERC_DEFLATE',
        'bandnum': 1,
    }

    mask_ds = ds(path=tpath, copypath=path2raster, options=options, overwrite=overwrite, editable=True)

    band_list = list(range(1, s_ds.RasterCount+1))
    mask_array = None

    if alpha is not None:
        alpha = int(alpha)
        if (alpha>0 and alpha<=s_ds.RasterCount):
            mask_array = s_ds.GetRasterBand(alpha).ReadAsArray().astype(np.bool)
            band_list.pop(alpha+1)

    if mask_array is None:
        mask_array = np.ones((s_ds.RasterYSize, s_ds.RasterXSize)).astype(np.bool)

    if use_nodata or (enforce_nodata is not None):
        for band in RasterData(path2raster).getting(1, band_order=band_list):
            band_array = None
            if use_nodata and (band.GetNoDataValue() is not None):
                band_array = band.ReadAsArray()
                mask_array[band_array==band.GetNoDataValue()] = False
            if enforce_nodata is not None:
                if band_array is None:
                    band_array = band.ReadAsArray()
                mask_array[band_array==enforce_nodata] = False
            band_array = None

    mask_band = mask_ds.GetRasterBand(1)

    mask_band.WriteArray(mask_array)

    shp_ds = shp(path2export, editable = True)
    lyr = shp_ds.GetLayer()

    # save_raster(path2export[:-4] + '.tif', mask_array, copypath=tpath, compress='LERC_DEFLATE', overwrite=True)

    gdal.Polygonize(mask_band, mask_band, lyr, 0, [], callback=gdal.TermProgress_nocb)
    shp_ds = None

    # Write projection
    write_prj(path2export[:-4] + '.prj', s_ds.GetProjection())

    return 0

def MultiplyRasterBand(bandpath_in, bandpath_out, multiplicator, dt = None, compress = None, overwrite = True):

    path_in, bandnum_in = bandpath_in
    path_out, bandnum_out = bandpath_out

    s_ds = gdal.Open(path_in)
    if s_ds is None:
        return 1

    if check_exist(path_out):
        if not overwrite:
            return 1
        ds_out = gdal.Open(path_out, 1)
    else:
        options = {
            'compress': compress,
            'bandnum': bandnum_out,
        }
        if dt is not None:
            options['dt'] = dt
        ds_out = ds(path=path_out, copypath=path_in, options=options, overwrite=overwrite, editable=True)

    raster_array = s_ds.GetRasterBand(bandnum_in).ReadAsArray()
    raster_array = raster_array * multiplicator
    ds_out.GetRasterBand(bandnum_out).WriteArray(raster_array)

    ds_out = None

    return 0


''' VECTOR PROCESSING FUNCTIONS '''



# Unites geometry from shapefiles
def Unite(path2shp_list, path2export, proj=None, overwrite=True):

    if check_exist(path2export, ignore=overwrite):
        return 1

    t_geom = None

    for path2shp in path2shp_list:

        s_ds = ogr.Open(path2shp)

        if s_ds is None:
            continue

        s_lyr = s_ds.GetLayer()

        if s_lyr is None:
            continue

        if proj is None:
            proj = s_lyr.GetSpatialRef().ExportToWkt()

        for feat in s_ds.GetLayer():

            if t_geom is None:
                o_feat = feat
                t_geom = o_feat.GetGeometryRef()
            else:
                # o_geom = t_geom
                n_geom = feat.GetGeometryRef()
                # print('in')
                t_geom = t_geom.Union(n_geom)
                # print('out')

    return Geom2Shape(path2export, t_geom, proj=proj)

    # t_feat_defn = ogr.FeatureDefn()
    t_feat = ogr.Feature(ogr.FeatureDefn())
    t_feat.SetGeometry(t_geom)

    shp_ds = shp(path2export, editable=True)
    lyr = shp_ds.GetLayer()
    lyr.CreateFeature(t_feat)

    shp_ds = None

    # Write projection
    write_prj(path2export[:-4] + '.prj', proj)

    return 0

# Returns intersection of two polygons in two different shapefiles of length == 1
def IntersectCovers(path2shp1, path2shp2, path2export, proj=None, overwrite=True):

    if check_exist(path2export, ignore=overwrite):
        return 1

    shp1_ds = ogr.Open(path2shp1)
    if shp1_ds is None:
        print('Cannot open shapefile: {}'.format(path2shp1))
        return 1

    shp2_ds = ogr.Open(path2shp2)
    if shp2_ds is None:
        print('Cannot open shapefile: {}'.format(path2shp2))
        return 1

    if (len(shp1_ds)!=1) or (len(shp2_ds)!=1):
        print('Each shape must have one polygon!')
        return 1

    lyr1 = shp1_ds.GetLayer()
    feat1 = lyr1.GetNextFeature()
    geom1 = feat1.GetGeometryRef()

    lyr2 = shp2_ds.GetLayer()
    feat2 = lyr2.GetNextFeature()
    geom2 = feat2.GetGeometryRef()

    if geom1.Intersects(geom2):

        t_geom = geom1.Intersection(geom2)

        # Deletes all geometry types except MultiPolygons
        t_geom = del_geom_by_type(t_geom, 6)

        if proj is None:
            proj = lyr1.GetSpatialRef().ExportToWkt()

        return Geom2Shape(path2export, t_geom, proj)

    else:
        print('Source geometries dont intersect')
        return 1

# Writes a single geometry object to a single shapefile without attributes
def Geom2Shape(path2export, geom, proj=None):
    t_feat = ogr.Feature(ogr.FeatureDefn())
    t_feat.SetGeometry(geom)
    shp_ds = shp(path2export, editable=True)
    lyr = shp_ds.GetLayer()
    lyr.CreateFeature(t_feat)
    shp_ds = None
    if proj is not None:
        write_prj(path2export[:-4] + '.prj', proj)
    return 0

def del_geom_by_type(old_geom, type):
    if old_geom.GetGeometryType == type:
        return old_geom
    else:
        new_geom = ogr.Geometry(type)
        for geom in old_geom:
            new_geom.AddGeometry(geom)
        return new_geom

def feature_fid(lyr):
    fid_list = [-1]
    for feat in lyr:
        fid = feat.GetFID()
        if fid in fid_list:
            fid = max(fid_list) + 1
        fid_list.append(fid)
    fid_list.pop(0)
    return fid_list

def add_fid(feat, fid_list):
    fid = feat.GetFID()
    if fid in fid_list:
        fid = max(fid_list) + 1
    fid_list.append(fid)
    return fid, fid_list

# Get feature data as dictionary
def feature_dict(feat, keys=None, geom_col_name=None, rep_keys_dict=None):

    if keys is None:
        keys = feat.keys()
    else:
        keys = obj2list(keys)

    if rep_keys_dict is not None:
        feat_rep_keys_dict = {}
        for key in rep_keys_dict.key():
            if key in keys:
                feat_rep_keys_dict[key] = rep_keys_dict[key]
        if len(feat_rep_keys_dict) == 0:
            feat_rep_keys_dict = None
    else:
        feat_rep_keys_dict = None

    attr_dict = OrderedDict()

    for key in keys:
        if feat_rep_keys_dict is not None:
            fin_key = feat_rep_keys_dict.get(key, key)
            attr_dict[fin_key] = feat.GetField(key)
        else:
            # print(key, feat.GetFieldIndex(key))
            attr_dict[key] = feat.GetField(key)
        # print('{}: {}'.format(key, type(feat.GetField(key))))

    if geom_col_name is not None:
        attr_dict[geom_col_name] = feat.GetGeometryRef()

    return attr_dict

# Get feature data type as dictionary
def feature_data_type_dict(feat, keys=None):

    if keys is None:
        keys = feat.keys()
    else:
        keys = obj2list(keys)

    attr_dict = OrderedDict()

    dt_dict = OrderedDict()

    for key in feat.keys():
        dt_dict[key] = feat.GetFieldType(key)

    return dt_dict

# Get column data as ordered dictionary
def column_dict(lyr, key, default = None):

    col_dict = OrderedDict()

    fid_list = lyr.GetFIDColumn()

    for feat in lyr:

        fid = feat.GetFID(key)
        if fid == (-1):
            fid = max(fid_list) + 1
            fid_list.append(fid)

        value = feat.GetField(key)
        if value is None:
            value = default

        col_dict[fid] = value

    return col_dict

# Get layer data as ordered dictionary
def layer_column_dict(lyr, columns=None, geom_col_name=None, lyr_defn_name=None, field_defn_col_name=None, columns_as_arrays=False):

    fid_list = [-1]

    if columns is None:
        key_list = []
    else:
        key_list = obj2list(columns)                    # !!!! It's better to preserve predefined geometry column names

    if geom_col_name is not None:
        key_list.append(geom_col_name)

    rep_keys_dict = forbid_names_dict(geom_col_name=None, lyr_defn_name=None, field_defn_col_name=None, orignames=key_list)
    # The new key list is created here to avoid mistakes if different features would have different column names
    # If a feature has column name same as one of new_names from rep_keys_dict, this date would be lost
    # To avoid this it's better to create keys list before using the function

    lyr_dict = OrderedDict()
    lyr.ResetReading()

    for i, feat in enumerate(lyr):

        # fid, fid_list = add_fid(feat, fid_list)
        # print(columns)
        feat_dict = feature_dict(feat, keys=columns, geom_col_name=geom_col_name, rep_keys_dict=rep_keys_dict)
        # print(columns)

        if columns is None:
            new_key_list = feat_dict.keys()
            for key in new_key_list:
                if key not in key_list:
                    key_list.append(key)

        for key in key_list:
            if key in lyr_dict:
                lyr_dict[key].append(feat_dict[key])
            else:
                new_col_list = listfull(i, None)
                new_col_list.append(feat_dict[key])
                lyr_dict[key] = new_col_list

    if (lyr_defn_name is not None) or (field_defn_col_name is not None):
        feat_defn = lyr.GetLayerDefn()

        if lyr_defn_name is not None:
            lyr_dict[lyr_defn_name] = feat_defn

        if field_defn_col_name is not None:
            field_defn_dict = {}
            for key in key_list:
                field_id = feat_defn.GetFieldIndex(key)
                if field_id != (-1):
                    field_defn_dict[key] = feat_defn.GetFieldDefn(field_id)
            lyr_dict[field_defn_col_name] = field_defn_dict

    if columns_as_arrays:
        for key in lyr_dict:
            if isinstance(lyr_dict[key], list):
                lyr_dict[key] = np.array(lyr_dict[key])

    return lyr_dict

# Get layer from vector file
def get_lyr_by_path(path, editable = False):

    ds = ogr.Open(path, editable)

    if ds is None:
        print('Cannot open file: {}'.format(path))
        return (None, None)

    lyr = ds.GetLayer()

    if lyr is None:
        print('Cannot get layer from: {}'.format(path))

    return (ds, lyr)


def JoinShapesByAttributes(path2shape_list,
                           path2export,
                           attributes = None,
                           new_attributes = None,     # {new_attr1_key: (attr1_key, function1, new_field1_defn),
                                                            #  new_attr2_key: (attr2_key, function2, new_field2_defn),
                                                            #  new_attr3_key: (attr1_key, function3, new_field3_defn),}
                           geom_rule = 0,
                           attr_rule = 0,
                           attr_rule_dict = {},
                           overwrite = True):

    if check_exist(path2export, ignore=overwrite):
        return 1

    if attributes is not None:
        attributes = obj2list(attributes)

    new_attr_call = isinstance(new_attributes, NewFieldsDict)

    # t_ds = shp(path2export, editable=True)
    t_ds = json(path2export, editable=True) # It's better to use json because ESRI_Shapefile works incorrectly with long field names
    t_lyr = t_ds.GetLayer()

    attr_val_list = []
    feat_num = 0

    for path2shape in path2shape_list:

        # print('Started %s' % path2shape)

        s_ds, s_lyr = get_lyr_by_path(path2shape)

        if s_lyr is None:
            continue

        for feat in s_lyr:

            keys = feat.keys()

            attr_check = []

            # Collect all the attributes or add each new feature separately if attributes are not defined
            if attributes is None:
                attr_check.append(feat_num)
                feat_num += 1
            else:
                for attribute in attributes:
                    if attribute in keys:
                        attr_check.append(feat.GetField(attribute))
                    else:
                        attr_check = None
                        break

            if (attr_check is not None) and new_attr_call:
                new_attr = new_attributes.ValuesList(feat)
                attr_check.extend(new_attr)

            # print(attr_check)

            if attr_check is not None:

                if attr_check in attr_val_list:

                    # Mix two features
                    feat_id = attr_val_list.index(attr_check)
                    t_ds = None
                    t_ds = ogr.Open(path2export, 1)
                    t_lyr = t_ds.GetLayer()
                    old_feat = t_lyr.GetFeature(feat_id)
                    if old_feat is not None:
                        new_feat = join_feature(old_feat, feat, geom_rule=geom_rule, attr_rule=attr_rule, attr_rule_dict=attr_rule_dict, ID=feat_id)
                    else:
                        new_feat = None
                    if new_feat is not None:
                        # print(new_feat.GetFID())
                        if new_attr_call:
                            # new_feat = new_attributes.AddFields(new_feat, new_attr)
                            new_feat = new_attributes.AddFields(new_feat)
                        t_lyr.SetFeature(new_feat)
                    else:
                        print('Cannot make new feature')

                else:

                    # Add a new feature
                    attr_val_list.append(attr_check)
                    feat_id = attr_val_list.index(attr_check)
                    feat.SetFID(-1) # Works correctly with json only if original FID is deleted. The field is found by its location
                    if new_attr_call:
                        # feat = new_attributes.AddFields(feat, new_attr)
                        feat = new_attributes.AddFields(feat)
                    t_lyr.CreateFeature(feat)

    t_ds = None

    if new_attributes is not None:
        print(new_attributes.add)

    return 0

def TimeCovers(path2vec, path2export, time_column, sort_columns=None, time_limit=0, min_area=0, attr_rule=0, overwrite = True):

    if check_exist(path2export, ignore=overwrite):
        return 1

    s_ds, s_lyr = get_lyr_by_path(path2vec)

    if s_lyr is None:
        return 1

    vec_dict = layer_column_dict(s_lyr, geom_col_name='geom_')

    for i, acq_date in enumerate(vec_dict.get('acquired')):
        vec_dict['date'][i] = int(str(acq_date)[:10].replace(r'/', ''))
    # scroll(vec_dict['date'])

    keys_list = list(vec_dict.keys())
    keys_list.pop(keys_list.index('geom_'))

    times = np.array(vec_dict.get(time_column))
    geoms = np.array(vec_dict.get('geom_'))

    data_list = [geoms, times]

    if sort_columns is not None:
        for key in sort_columns:
            new_col = vec_dict.get(key)
            if new_col is not None:
                data_list.append(np.array(new_col))
    else:
        sort_columns = keys_list

    # data_array = np.vstack(data_list)

    # times_array = np.array(times)
    times_list = list(np.unique(times))
    times_list.sort()
    # times_list.reverse()

    upper_cover_dict = OrderedDict()
    daily_cover_geom_dict = OrderedDict()

    export_cover_dict = OrderedDict()
    export_cover_dict['geom_'] = []

    for key in keys_list:
        export_cover_dict['%s_old' % key] = []
        export_cover_dict['%s_new' % key] = []

    # scroll(times_list)

    for date in times_list:

        print(date)

        source_date_dict = OrderedDict()

        for key in (keys_list + ['geom_']):
            source_date_dict[key]=[]
        add_ids = []
        for id, scene_date in enumerate(times):
            if scene_date == date:
                add_ids.append(id)
        for add_id in add_ids:
            source_date_dict['geom_'].append(vec_dict['geom_'][add_id])
            for key in keys_list:
                source_date_dict[key].append(vec_dict[key][add_id])

        # date_filter = data_array[1] == date
        # date_data = data_array[:, date_filter]

        # full_cover_geom, cover_lyr = make_cover(date_data, 'geom_', sort_columns)
        # scroll(source_date_dict.keys())
        # scroll(source_date_dict['date'])

        full_cover_geom, cover_lyr = make_cover(source_date_dict, 'geom_', sort_columns)

        # scroll(source_date_dict['date'])

        daily_cover_geom_dict[date] = full_cover_geom

        # scroll(source_date_dict['date'])

        if len(upper_cover_dict)==0:
            upper_cover_dict = cover_lyr
            continue

        # scroll(source_date_dict['date'])

        for under_id, under_geom in enumerate(cover_lyr['geom_']):

            for upper_id, upper_geom in enumerate(upper_cover_dict['geom_']):

                if (upper_cover_dict.get(time_column)[upper_id] - upper_cover_dict.get(time_column)) < time_limit:

                    if upper_geom.Intersect(under_geom):

                        intersect_geom = upper_geom.Intersection(under_geom)

                        if intersect_geom.Area() > min_area:

                            export_cover_dict['geom_'].append(intersect_geom)
                            upper_cover_dict['geom_'].append(intersect_geom)

                            for key in keys_list:
                                export_cover_dict['%s_new' % key].append(upper_cover_dict[key][upper_id])

                            if intersect_geom.Equals(upper_geom):
                                for key in upper_cover_dict:
                                    upper_cover_dict[key].pop(upper_id)
                            else:
                                upper_cover_dict['geom_'][upper_id] = upper_geom.Difference(intersect_geom)

                            for key in keys_list:
                                value = cover_lyr.get(key)[under_id]
                                upper_cover_dict[key].append(value)
                                export_cover_dict['%s_old' % key].append(value)

                            if intersect_geom.Equals(under_geom):
                                break
                            else:
                                under_geom = under_geom.Difference(intersect_geom)

    if len(export_cover_dict['geom_']) > 0:
        exp_ds = json(path2export, 1)
        exp_lyr = json.GetLayer()

        exp_lyr_defn = s_lyr.GetLayerDefn()
        new_keys = []

        for key in keys_list:
            field_id = exp_lyr_defn.GetFieldIndex(key)
            new_field_defn = exp_lyr_defn.GetFieldDefn(field_id)

            old_new_key = '%s_old' % key
            exp_lyr.CreateField(new_field_defn.SetName('%s_old' % key))
            new_keys.append(old_new_key)

            new_new_key = '%s_new' % key
            exp_lyr.CreateField(new_field_defn.SetName('%s_new' % key))
            new_keys.append(new_new_key)

        exp_ds = None
        exp_ds, exp_lyr = get_lyr_by_path(path2export, 1)
        feat_defn = exp_lyr

        for feat_id, feat_geom in range(export_cover_dict['geom_']):

            feat_attr = OrderedDict()

            for key in new_keys:
                feat_attr[key] = export_cover_dict.get(key)[feat_id]

            feat = feature(feat_defn, geom=feat_geom, attr=feat_attr)

            exp_lyr.CreateFeature(feat)

        exp_ds = None

    return 0

def make_cover(lyr_dict, geom_col_name, sort_columns, save_columns=None, new_columns=None):

    if geom_col_name in lyr_dict:
        geom_list = lyr_dict[geom_col_name]
    else:
        print ('No geometry column found, unable to build cover')
        return None


    # scroll(geom_list)

    sort_col_list = []
    for sort_col_name in sort_columns:
        if sort_col_name in lyr_dict:
            sort_col_list.append(list(lyr_dict[sort_col_name]))

    if len(sort_col_list) == 0:
        print('No sorting columns found')
        return None

    order_list = sort_multilist(sort_col_list)

    if save_columns is None:
        save_columns = list(lyr_dict.keys())
        save_columns.pop(save_columns.index(geom_col_name))

    save_col_list = []
    for col_name in save_columns:
        if col_name in lyr_dict:
            if isinstance(lyr_dict[col_name], list):
                save_col_list.append(col_name)

    cover_lyr = OrderedDict()
    cover_lyr['geom_'] = []

    for col_name in save_col_list:
        cover_lyr[col_name] = []

    full_cover_geom = None

    # scroll(lyr_dict['date'])

    print(order_list)

    print(geom_list[0:1])

    for id in order_list:

        new_geom = geom_list[id]

        print(new_geom)

        if full_cover_geom is None:
            add = True
            full_cover_geom = new_geom
        else:
            add = full_cover_geom.Contains(new_geom)

        if add:
            cover_lyr[geom_col_name].append(new_geom.Difference(full_cover_geom))
            full_cover_geom = full_cover_geom.Union(new_geom)
            for col_name in save_col_list:
                cover_lyr[col_name] = lyr_dict[col_name][id]

    scroll(lyr_dict['date'])

    return full_cover_geom, cover_lyr

def join_feature(feat1, feat2, geom_rule = 0, attr_rule = 0, attr_rule_dict = {}, attr_list=None, ID = None):

    geom1 = feat1.GetGeometryRef()
    geom2 = feat2.GetGeometryRef()

    if geom_rule == 0:
        new_geom = geom1.Intersection(geom2)
    elif geom_rule == 1:
        new_geom = geom1.Union(geom2)
    elif geom_rule == 2:
        new_geom = geom1.Difference(geom2)
    elif geom_rule == 3:
        new_geom = geom1.SymmetricDifference(geom2)
    # elif geom_rule == 4:
        # new_geom = geom1.UnionCascaded(geom2)
    else:
        print('Unreckognized geom_rule: {}'.format(geom_rule))
        return None

    new_attr_dict = feature_dict(feat1)
    join_attr_dict = feature_dict(feat2)

    if attr_list is None:
        attr_list = new_attr_dict.keys()

    for i, key in enumerate(new_attr_dict):

        join_attr_val = join_attr_dict.get(key)

        if join_attr_val is None:
            continue
        else:
            old_attr_val = new_attr_dict.get(key)

        rule = attr_rule_dict.get(key, attr_rule)

        try:
            new_attr_dict[key] = ruled_operator(old_attr_val, join_attr_val, rule)
        except:
            new_attr_dict[key] = old_attr_val

    new_feat = feature(feature_defn=feat1.GetDefnRef(), geom=new_geom, attr=new_attr_dict)

    # print(new_feat.GetFID())
    if ID is not None:
        new_feat.SetFID(ID)
    else:
        new_feat.SetFID(feat1.GetFID())
    # print(new_feat.GetFID())

    return new_feat

def ruled_operator(x, y, rule, x_weight = 1, y_weight = 1):

    # 0 - Save old value
    if rule == 0:
        result = x
    # 1 - Save new value
    elif rule == 1:
        result = y
    # 2 - Save sum
    elif rule == 2:
        result = x + y
    # 3 - Save difference
    elif rule == 3:
        result = x - y
    # 4 - Save production
    elif rule == 4:
        result = x * y
    # 5 - Save ratio
    elif rule == 5:
        result = x / y
    # 6 - Save exponent
    elif rule == 6:
        result = x ** y
    # 7 - Save logarithm
    elif rule == 7:
        result = math.log(x,y)
    # 8 - Save mean
    elif rule == 8:
        result = (x + y) / 2
    # 9 - Save geometric mean
    elif rule == 9:
        result = (x * y) ** 0.5

    # 100 - Save weighted mean
    elif rule == 100:
        result = (x * x_weight + y * y_weight) / (x_weight + y_weight)

    else:
        print('Unreckognized attr_rule: {}'.format(rule))
        result = x

    return result

def feature(feature_defn = None, geom = None, attr = None, attr_type = 0, attr_type_dict = {}, ID = None):

    if feature_defn is None:
        feature_defn = ogr.FeatureDefn()

    # feat = ogr.Feature(ogr.FeatureDefn(geom_type))
    feat = ogr.Feature(feature_defn)

    if ID is not None:
        feat.SetFID(ID)

    if geom is not None:
        feat.SetGeometry(geom)

    if attr is not None:
        '''
        for key in attr.keys():
            val = attr[key]

            field_id = feature_defn.GetFieldIndex(key)
            # print(field_id)
            if field_id != (-1):
                feat.SetField(key, attr[key])
        '''

        for i, key in enumerate(feat.keys()):

            if key in attr.keys():
                feat.SetField(key, attr[key])
            else:
                feat.SetFieldNull(key)

    return feat

# Unites geometry data from list into new geometry
def unite_geom_list(geom_list):

    old_geom = deepcopy(geom_list[0])

    for new_geom in geom_list[1:]:
        old_geom = old_geom.Union(new_geom)

    return old_geom

# Returns geometry from layer
def geom_from_layer(ds, unite_geom = False, filter_field = None, filter_values = None):

    lyr = ds.GetLayer()
    geom_list = []
    filter = None

    if (filter_field is not None) and (filter_values is not None):
        if lyr.GetLayerDefn().GetFieldIndex(filter_field) != (-1):
            filter = obj2list(filter_values)

    for feat in lyr:
        if filter is not None:
            if feat.GetField(filter_field) not in filter:
                continue
        geom_list.append(feat.GetGeometryRef())

    print(geom_list)

    if unite_geom:

        return unite_geom_list(geom_list)
    else:
        return geom_list


# Returns coordinates of all points in geometry as a list of tuples with two float numbers in each
def geometry_points(geom):

    cpwkt = geom.ExportToWkt()
    coord_list = cpwkt.split(',')

    for i, coord in enumerate(coord_list):
        while '(' in coord:
            coord = coord[coord.index('(') + 1:]
        while ')' in coord:
            coord = coord[:coord.index(')')]
        y, x = coord.split(' ')
        y = float(y)
        x = float(x)
        coord_list[i] = (y, x)

    return coord_list


# Estimates maximum length of line within polygon
def max_line_length(polygon):

    # !!! Not mathematically correct but works for now !!!
    coord_list = geometry_points(polygon)
    len_max = 0

    for i, coord1 in enumerate(coord_list):

        # print(coord1)
        y1, x1 = coord1

        for coord2 in coord_list[i+1:]:

            # print(coord2)
            y2, x2 = coord2
            # print(math.sqrt((x1-x2)**2+(y1-y2)**2))
            line_new = ogr.Geometry(wkt='LINESTRING ({y1} {x1}, {y2} {x2})'.format(x1=x1, y1=y1, x2=x2, y2=y2))
            len_new = line_new.Length()
            # print(len_new, line_new.ExportToWkt(), line_new.Within(polygon))

            if len_new > len_max:
                if line_new.Within(polygon):
                    # print(len_new, line_new.ExportToWkt())
                    len_max = len_new

    return len_max

# Creates random point whithin polygon as geometry
def random_point_geom(extent, border_geom):

    y_min, y_max, x_min, x_max = extent

    dx = x_max - x_min
    dy = y_max - y_min

    while True:

        x = x_min + dx * np.random.random()
        y = y_min + dy * np.random.random()
        new_point = ogr.Geometry(wkt = 'POINT ({y} {x})'.format(x=x, y=y))

        # print(extent, new_point.ExportToWkt())

        if border_geom.Intersects(new_point):
            return new_point

# Creates random line whithin given polygon
def random_line_geom(extent, border_geom, azimuth=None, length=None):

    y_min, y_max, x_min, x_max = extent

    dx = x_max - x_min
    dy = y_max - y_min

    if azimuth is None:
        azimuth = 2 * math.pi * np.random.random()

    if length is None:
        length = 0.1 * max_line_length(border_geom)

    while True:

        x1 = x_min + dx * np.random.random()
        y1 = y_min + dy * np.random.random()
        x2 = x1 + length * math.cos(azimuth)
        y2 = y1 + length * math.sin(azimuth)
        new_line = ogr.Geometry(wkt='LINESTRING ({y1} {x1}, {y2} {x2})'.format(x1=x1, y1=y1, x2=x2, y2=y2))

        if border_geom.Contains(new_line):
            return new_line

# Returns orthogonal line by three point coordinate values
def random_rectangle_line(x1, y1, dx2, dy2, dx3, dy3):

    random_num = np.random.random()

    x2 = x1 + dx2 * random_num
    y2 = y1 + dy2 * random_num

    x3 = x2 + dx3
    y3 = y2 + dy3

    line_geom = ogr.Geometry(wkt = 'LINESTRING ({y2} {x2}, {y3} {x3})'.format(x2=x2, y2=y2, x3=x3, y3=y3))

    return line_geom

# Creates a predefined number of random points within defined area
def RandomPointsInside(path_in, path_out, points_num=100, overwrite=True):

    if check_exist(path_out, ignore=overwrite):
        return 1

    ds_in, lyr_in = get_lyr_by_path(path_in)

    if lyr_in is None:
        return 1

    if len(lyr_in) <= 0:
        return 1

    geom_list = []

    for feat in lyr_in:
        geom_list.append(feat.GetGeometryRef())

    border_geom = unite_geom_list(geom_list)

    # print(border_geom.ExportToWkt())

    geom_list = None

    ds_out = shp(path_out, 1)
    lyr_out = ds_out.GetLayer()

    point_feat_defn = lyr_out.GetLayerDefn()

    y_min, y_max, x_min, x_max = extent = lyr_in.GetExtent()

    for i in range(points_num):

        new_point_geom = random_point_geom(extent, border_geom)
        new_point_feat = feature(point_feat_defn, new_point_geom)
        lyr_out.CreateFeature(new_point_feat)

    ds_out = None

    write_prj(path_out[:-4] + '.prj', lyr_in.GetSpatialRef().ExportToWkt())

    return 0


def RandomLinesInside(path_in, path_out, lines_num = 100, azimuth = None, length = None, random_azimuth = False, overwrite = True):

    if check_exist(path_out, ignore=overwrite):
        return 1

    ds_in, lyr_in = get_lyr_by_path(path_in)

    if lyr_in is None:
        return 1

    if len(lyr_in) <= 0:
        return 1

    geom_list = []

    for feat in lyr_in:
        geom_list.append(feat.GetGeometryRef())

    border_geom = unite_geom_list(geom_list)

    geom_list = None

    if (azimuth is None) and (random_azimuth == False):
        azimuth = 2 * math.pi * np.random.random()

    if length is None:
        length = 0.1 * max_line_length(border_geom)

    ds_out = shp(path_out, 1)
    lyr_out = ds_out.GetLayer()

    point_feat_defn = lyr_out.GetLayerDefn()

    extent = lyr_in.GetExtent()

    for i in range(lines_num):

        new_point_geom = random_line_geom(extent, border_geom, azimuth=azimuth, length=length)
        new_point_feat = feature(point_feat_defn, new_point_geom)
        lyr_out.CreateFeature(new_point_feat)

    ds_out = None

    write_prj(path_out[:-4] + '.prj', lyr_in.GetSpatialRef().ExportToWkt())

    return 0

def RandomLinesRectangle(path_in, path_out,
                         lines_num = 100,
                         path_patches = None,
                         filter_field = 'KOD',
                         filter_values = None,
                         invert_axis = False,
                         overwrite = True):

    if check_exist(path_out, ignore=overwrite):
        return 1

    ds_in, lyr_in = get_lyr_by_path(path_in)

    if lyr_in is None:
        return 1

    if len(lyr_in) != 1:
        return 1

    rectangle_feat = lyr_in.GetNextFeature()
    rectangle_geom = rectangle_feat.GetGeometryRef()

    if invert_axis:
        p3, p2, p1 = geometry_points(rectangle_geom)[:3]
    else:
        p1, p2, p3 = geometry_points(rectangle_geom)[:3]

    y1, x1 = p1
    y2, x2 = p2
    y3, x3 = p3

    dx2 = x2 - x1
    dy2 = y2 - y1

    dx3 = x3 - x2
    dy3 = y3 - y2

    ds_out = shp(path_out, 1)
    lyr_out = ds_out.GetLayer()

    if path_patches is not None:

        ds_patches, lyr_patches = get_lyr_by_path(path_patches)
        lyr_out.CreateField(ogr.FieldDefn('Intersect', ogr.OFTInteger))

        filter = None
        if (filter_field is not None) and (filter_values is not None):
            if filter_field in lyr_patches.next().keys():
                filter = obj2list(filter_values)

    else:
        lyr_patches = None

    line_feat_defn = lyr_out.GetLayerDefn()


    for i in range(lines_num):

        new_line_geom = random_rectangle_line(x1, y1, dx2, dy2, dx3, dy3)
        # print(new_line_geom.ExportToWkt())
        new_line_feat = feature(line_feat_defn, new_line_geom)

        if lyr_patches is not None:

            intersect = 0

            lyr_patches.ResetReading()
            for feat in lyr_patches:
                # print(new_line_geom.Intersect(feat.GetGeometryRef()))
                # print(feat.GetGeometryRef().ExportToWkt())
                if filter is not None:
                    if feat.GetField(filter_field) not in filter:
                        continue
                if new_line_geom.Intersect(feat.GetGeometryRef()):
                    intersect = 1
                    break

            new_line_feat.SetField('Intersect', intersect)

        lyr_out.CreateFeature(new_line_feat)

    lyr_out.ResetReading()
    print(lyr_out.next().keys())

    ds_out = None

    write_prj(path_out[:-4] + '.prj', lyr_in.GetSpatialRef().ExportToWkt())

    return 0

# Rasterize vector layer
# Returns a mask as np.array of np.bool
def RasterizeVector(path_in_vector, path_in_raster, path_out, compress = None, overwrite=True):

    if check_exist(path_out, ignore=overwrite):
        return 1

    options = {
        'dt': 1,
        'nodata': 0,
        'compress': compress,
        'bandnum': 1,
    }

    t_ds = ds(path=path_out, copypath=path_in_raster, options=options, editable=True, overwrite=overwrite)
    ds_in_vector, lyr_in_vector = get_lyr_by_path(path_in_vector)

    if lyr_in_vector is None:
        return 1

    try:
        s = gdal.RasterizeLayer(t_ds, [1], lyr_in_vector, burn_values=[1]) # This code raises warning if the layer does not have a projection definition
    except:
        print('No pixels to filter in vector mask')

    t_ds = None

    return 0

# Calculates values for new fields in GDAL features preserving FieldDefn data if nessessary
class NewFieldsDict():

    def __init__(self):
        self.keys = []
        self.input_keys = OrderedDict()
        self.functions = OrderedDict()
        self.fields = OrderedDict()
        self.defaults = OrderedDict()
        self.add = OrderedDict()

    def __bool__(self):
        return bool(len(self))

    # Define a new field generator
    def NewField(self, key, input_key, func, field_defn = None, default_value = None, add = False):

        if key in self.keys:
            index = self.keys.index(key)
            self.keys.pop(index)
            self.keys.insert(index, key)
        else:
            self.keys.append(key)

        assert isinstance(input_key, str)
        assert hasattr(func, '__call__')


        self.input_keys[key] = input_key
        self.functions[key] = func
        self.fields[key] = field_defn
        self.defaults[key] = default_value
        self.add[key] = bool(add)

    def CheckNaming(self, check_names = None):

        if hasattr(check_names, '__iter__'):
           for key in self.keys:
                if key in self.input_keys:
                    print('Wrong naming, cannot add field: {}'.format(key))
                    self.add[key] = False

    # Returns a value of a function
    def Value(self, key, input_value):
        if key in self.keys:
            try:
                return self.functions.get(key)(input_value)
            except:
                return self.defaults.get(key)

    # Returns a list of values for a feature
    def ValuesList(self, feat):

        val_list = []

        for key in self.keys:
            input_value = feat.GetField(self.input_keys[key]) or None
            if input_value is not None:
                val_list.append(self.Value(key, input_value))
            else:
                val_list.append(None)

        return val_list

    def AddFields(self, feat, new_fields = {}):

        for key in self.keys:
            if self.add[key]:
                new_value = new_fields.get(key)
                if new_value is None:
                    input_value = feat.GetField(self.input_keys[key]) or None
                    new_value = self.Value(key, input_value)
                feat.SetField(key, input_value)

        return feat
