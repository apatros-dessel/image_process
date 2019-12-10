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

import calc

from limb import tdir, default_temp, listfull, newname

temp_dir_list = tdir(default_temp)

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
def save_raster(path, band_array, copypath = None, proj = None, trans = None, dt = None, nodata = None):
    if copypath is not None:
        copy_ds = gdal.Open(copypath)
        if proj is None:
            proj = copy_ds.GetProjection()
        if trans is None:
            trans = copy_ds.GetGeoTransform()
        if nodata is None:
            nodata = copy_ds.GetRasterBand(1).GetNoDataValue()
    band_array = calc.array3dim(band_array)
    if dt is None:
        dt = format_to_gdal(band_array.dtype)
    xsize = len(band_array[0][0])
    ysize = len(band_array[0])
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    outData = driver.Create(path, xsize, ysize, len(band_array), dt)
    for band_num in range(1, len(band_array)+1):
        outData.GetRasterBand(band_num).WriteArray(band_array[band_num-1])
        if nodata is not None:
            outData.GetRasterBand(band_num).SetNoDataValue(nodata)
    outData.SetProjection(proj)
    outData.SetGeoTransform(trans)
    outData = None
    return None
'''
    # Creates a new empty virtual Dataset in scene.data
    def add_dataset(self, data_id, copy=None, param=None, cell_size=None):
        data_id = str(data_id)
        if data_id in (list(self.file_names.keys()) + self.data_list):
            raise Exception('The dataset already exists: {}'.format(data_id))
        if cell_size is None:
            cell_size = self.cell_size[0]
        if copy is not None:
            if type(copy) == gdal.Dataset:
                x_res = copy.RasterXSize
                y_res = copy.RasterYSize
                proj = copy.GetProjection()
                trans = copy.GetGeoTransform()
                if copy.RasterCount > 0:
                    dtype = copy.GetRasterBand(1).DataType
                    num_bands = copy.RasterCount
            else:
                raise TypeError('copy = {} must be of type gdal.Dataset'.format(copy))
        else:
            y_res, x_res = self.array_shape[str(cell_size)]
            proj = self.projection
            trans = self.transform
            dtype = 1
            num_bands = 1
        if param is not None:
            y_res = param.get('y_res', y_res)
            x_res = param.get('x_res', x_res)
            proj = param.get('proj', proj)
            trans = param.get('trans', trans)
            dtype = param.get('dtype', dtype)
            num_bands = param.get('num_bands', num_bands)
        self.data[data_id] = create_virtual_dataset(proj, trans, (y_res, x_res), num_bands, dtype)
        self.data_list.append(data_id)
        return self.data[data_id]

    # Creates a new Dataset containing data from a band_array
    def array_to_dataset(self, data_newid, band_array, copy=None, param=None):
        band_array = array3dim(band_array)
        band_num = len(band_array)
        if param is None:
            param = {'num_bands': band_num}
        elif 'num_bands' not in param:
            param['num_bands'] = band_num
        self.add_dataset(data_newid, copy, param)
        for band_id in range(1, band_num+1):
            self.data[data_newid].GetRasterBand(band_id).WriteArray(band_array[band_id-1])
        self.data_list.append(data_newid)
        return self[data_newid]
'''
def clip_raster(path2raster, path2vector, export_path = None, byfeatures = True, exclude = False, nodata = 0, path2newshp = None):
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
    save_raster(export_path, raster_array, proj = crs_wkt, trans = tuple(geotrans), nodata = nodata)
    #save_raster(export_path, param)
    return None

# The code below has been take from 'merge_raster' plugin by S.Sadkov, I havent checked correspondence with other functions here
interpol_method = [gdal.GRA_NearestNeighbour, gdal.GRA_Average, gdal.GRA_Bilinear, gdal.GRA_Cubic, gdal.GRA_CubicSpline, gdal.GRA_Lanczos]

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

def band2raster(s_raster_path, t_raster, s_band_num, method, exclude_nodata = True, enforce_nodata = None):
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
    t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, dtype, method)
    t_raster.AddBand(dtype)
    if exclude_nodata:
        if enforce_nodata is None:
            enforce_nodata = s_raster.GetRasterBand(s_band_num).GetNoDataValue()
        if enforce_nodata is not None:
            t_raster.GetRasterBand(t_raster.RasterCount).SetNoDataValue(enforce_nodata)
    t_raster.GetRasterBand(t_raster.RasterCount).WriteArray(t_band_array)
    return t_raster.RasterCount

def raster2raster(path2start, path2target, path2export, band_nums = None, method = gdal.GRA_Bilinear, exclude_nodata = True, enforce_nodata = None):
    len_ = len(path2start)
    if band_nums is None:
        band_nums = listfull(len_, 1)
    elif type(band_nums) is int:
        band_nums = listfull(len_, band_nums)
    else:
        while len(band_nums) < len_:
            band_nums.append(band_nums[-1])
    t_raster = gdal.Open(path2target)
    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    ds = create_virtual_dataset(t_proj, t_trans, t_shape, 0)
    for id in range(len_):
        band2raster(path2start[id], ds, band_nums[id], method, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata)
    driver = gdal.GetDriverByName('GTiff')
    outputData = driver.CreateCopy(path2export, ds, len(band_nums))
    outputData = None
    return

# Calculates difference between two bands
def band_difference(path2raster, export_path, band1 = 1, band2 = 1, nodata = 0):
    raster_ds = gdal.Open(path2raster)
    if raster_ds is not None:
        band1_array = raster_ds.GetRasterBand(band1).ReadAsArray()
        band2_array = raster_ds.GetRasterBand(band2).ReadAsArray()
    band_fin = (band2_array - band1_array).reshape(tuple([1] + list(band1_array.shape)))
    # param = band_fin, raster_ds.GetProjection(), raster_ds.GetGeoTransform(), band_fin.dtype, nodata
    save_raster(export_path, band_fin, copypath = path2raster, nodata = nodata)
    return None

# Division of two bands with calculating percent of change
def percent(path2raster, export_path, band1 = 1, band2 = 1, nodata = 0):
    raster_ds = gdal.Open(path2raster)
    if raster_ds is not None:
        band1_array = raster_ds.GetRasterBand(band1).ReadAsArray().astype(np.float32)
        band2_array = raster_ds.GetRasterBand(band2).ReadAsArray().astype(np.float32)
    band_fin = ((band2_array / band1_array) * 100).reshape(tuple([1] + list(band1_array.shape)))
    band_fin[band_fin != 0] = band_fin[band_fin != 0] - 100
    param = band_fin, raster_ds.GetProjection(), raster_ds.GetGeoTransform(), band_fin.dtype, nodata
    save_raster(export_path, band_fin, copypath = path2raster, nodata = nodata)
    return None

# Saves data from a band in Dataset to polygon shapefile
def save_to_shp(path2raster, path2shp, band_num = 1, dst_fieldname = None, classify_table = None, export_values = None):

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
    print(path2raster)
    raster_ds = gdal.Open(path2raster)
    if classify_table is not None:
        band_array = calc.segmentator(raster_ds.GetRasterBand(band_num).ReadAsArray(), classify_table)
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
'''
def extent2shp(path2raster, path2shp):
    raster_ds = gdal.Open(path2raster)
    crs = osr.SpatialReference()
    crs.ImportFromWkt(raster_ds.GetProjection())
    trans = raster_ds.GetGeoTransform()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(path2shp)
    lyr = data_source.CreateLayer('Layer', crs, 'POLYGON')
    coords = np.zeros((4,2), dtype = float)
    coords[0,0] = trans[0]
    coords[0,1] = trans[3]
    coords[1,0] = trans[0] +
    for i in range(4):
        feat = ogr.Feature(lyr.GetLayerDefn())
        x =
'''

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
    print(path2bands)
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
def normalized_difference(path2bands, path2export, dt = None):
    data_array = getbandarrays(path2bands).astype(np.float)
    print(data_array.shape)
    # New option below
    mask = np.ones(data_array.shape[1:]).astype(np.bool)
    for slice in data_array:
        mask[slice==0] = False
    #nd_data = (data_array[1][mask] - data_array[0][mask]) / (data_array[1][mask] + data_array[0][mask])
    nd_array = np.zeros(data_array.shape[1:])
    nd_array[mask] = (data_array[0][mask] - data_array[1][mask]) / (data_array[1][mask] + data_array[0][mask])
    #nd_array = (data_array[1] - data_array[0]) / (data_array[1] + data_array[0])
    save_raster(path2export, nd_array, copypath = path2bands[0][0], dt = dt)
    return None

index_calculator = {
    'Normalized': normalized_difference,
}

def write_prj(path2prj, projection):
    prj_handle = open(path2prj, 'w')
    prj_handle.write(projection)
    prj_handle.close()
    return None

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

class bandpaths(list):

    def __init__(self, bandpath_list = []):
        # Add keys?
        pass

    def addband(self, band):
        if band is bandpath:
            self.append(band)
