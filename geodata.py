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

from tools import tdir, default_temp, newname, scroll, OrderedDict, check_exist, lget, deepcopy, list_of_len

from raster_data import RasterData, MultiRasterData

from calc import array3dim, segmentator, limits_mask, data_to_image, get_raster_limits

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

    print(options)

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


# Create ogr vector dataset
def shp(path2shp, dst_fieldname, editable = False):

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

    if dst_fieldname is None:
        dst_fieldname = 'DN'
    fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
    dst_layer.CreateField(fd)
    dst_field = 0

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

# Calculates difference between two bands
def band_difference(path2raster, export_path, band1 = 1, band2 = 1, nodata = 0, compress = None, overwrite = True):
    raster_ds = gdal.Open(path2raster)
    if raster_ds is not None:
        band1_array = raster_ds.GetRasterBand(band1).ReadAsArray()
        band2_array = raster_ds.GetRasterBand(band2).ReadAsArray()
    band_fin = (band2_array - band1_array).reshape(tuple([1] + list(band1_array.shape)))
    # param = band_fin, raster_ds.GetProjection(), raster_ds.GetGeoTransform(), band_fin.dtype, nodata
    res = save_raster(export_path, band_fin, copypath = path2raster, nodata = nodata, compress = compress, overwrite=overwrite)
    return res

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
def RasterDataMask(path2raster, path2export, use_nodata = True, enforce_nodata = None, alpha=None, dst_fieldname = None, overwrite = True):

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

    shp_ds = shp(path2export, dst_fieldname, editable = True)
    lyr = shp_ds.GetLayer()

    # save_raster(path2export[:-4] + '.tif', mask_array, copypath=tpath, compress='LERC_DEFLATE', overwrite=True)

    gdal.Polygonize(mask_band, mask_band, lyr, 0, [], callback=gdal.TermProgress_nocb)
    shp_ds = None

    # Write projection
    write_prj(path2export[:-4] + '.prj', s_ds.GetProjection())

    return 0

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

    shp_ds = shp(path2export, None, editable=True)
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
    shp_ds = shp(path2export, None, editable=True)
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