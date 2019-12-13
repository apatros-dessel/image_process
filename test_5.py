# Recalculates two DEMs' values to mince the mutual regression

import os
import gdal
import numpy as np

path = 'c:\\sadkov\\forest\\dem'
file_dem1 = r'relief_points_severnoye.shp'
file_dem2 = r'relief_labels_severnoye.shp'

# Reprojects raster band
def reproject_band(band, s_proj, s_trans, t_proj, t_trans, t_shape, method=gdal.GRA_Average, dtype=gdal.GDT_Byte):
    y_size, x_size = band.shape
    driver = gdal.GetDriverByName('MEM')
    s_ds = driver.Create('', x_size, y_size, 1, dtype)
    #s_ds.AddBand(dtype)
    s_ds.GetRasterBand(1).WriteArray(band)
    #print(np.unique(s_ds.GetRasterBand(1).ReadAsArray()))
    s_ds.SetGeoTransform(s_trans)
    s_ds.SetProjection(s_proj)
    t_ds = driver.Create('', t_shape[1], t_shape[0], 0)
    t_ds.AddBand(dtype)
    t_ds.SetGeoTransform(t_trans)
    t_ds.SetProjection(t_proj)
    gdal.ReprojectImage(s_ds, t_ds, None, None, method)
    return t_ds.ReadAsArray()

def band2raster(s_raster, t_raster, s_band_num=1, t_band_num=1, method=gdal.GRA_Average, dtype=None):
    s_proj = s_raster.GetProjection()
    s_trans = s_raster.GetGeoTransform()
    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    if s_band_num > s_raster.RasterCount:
        s_band_num = s_raster.RasterCount
    if t_band_num > t_raster.RasterCount:
        t_band_num = t_raster.RasterCount
    if dtype is None:
        dtype = s_raster.GetRasterBand(s_band_num).DataType
    s_band_array = s_raster.GetRasterBand(s_band_num).ReadAsArray()
    # For some reason reprojection takes time even if the rasters' parameters are the same
    if (s_proj == t_proj) and (s_trans == t_trans):
        t_band_array = s_band_array
    else:
        t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, method=method, dtype=dtype)
        #t_raster.AddBand(dtype)
    #t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, dtype, method)
    export_raster = create_virtual_dataset(t_proj, t_trans, t_shape, 1, dtype)
    export_raster.GetRasterBand(t_band_num).WriteArray(t_band_array)
    return export_raster

# Creates gdal virtual dataset for use within scene class
def create_virtual_dataset(proj, geotrans, shape_, num_bands, dtype):
    y_res, x_res = shape_
    ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, num_bands, dtype)
    ds.SetGeoTransform(geotrans)
    ds.SetProjection(proj)
    return ds

dem1_ds = gdal.Open(file_dem1)
dem1 = dem1_ds.GetRasterBand(1).ReadAsArray()

dem2_ds = gdal.Open(file_dem2)
dem2_repr = band2raster(dem2_ds, dem1_ds)
dem2 = dem2_repr.GetRasterBand(1).ReadAsArray()

