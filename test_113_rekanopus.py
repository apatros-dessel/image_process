from geodata import *

folder = r'\\172.21.195.2\exchanger\Nikolaev\pmi\test_segmentation\dop\Kanopus\\'

def MakeQuicklook(path_in, path_out, epsg = None, pixelsize = None, method = gdal.GRA_Average, overwrite = True):
    if check_exist(path_out, ignore=overwrite):
        return 1
    ds_in = gdal.Open(path_in)
    if ds_in is None:
        return 1
    srs_in = get_srs(ds_in)
    if epsg is None:
        srs_out = srs_in
    else:
        srs_out = get_srs(epsg)
    if srs_out.IsGeographic():
        pixelsize = pixelsize / 50000
    if srs_in != srs_out:
        t_raster_base = gdal.AutoCreateWarpedVRT(ds_in, srs_in.ExportToWkt(), srs_out.ExportToWkt())
        x_0, x, x_ang, y_0, y_ang, y = t_raster_base.GetGeoTransform()
        newXcount = int(math.ceil(t_raster_base.RasterXSize * (x / pixelsize)))
        newYcount = abs(int(math.ceil(t_raster_base.RasterYSize * (y / pixelsize))))
    else:
        x_0, x, x_ang, y_0, y_ang, y = ds_in.GetGeoTransform()
        newXcount = int(math.ceil(ds_in.RasterXSize * (x / pixelsize)))
        newYcount = abs(int(math.ceil(ds_in.RasterYSize * (y / pixelsize))))
    options = {
        'dt':       ds_in.GetRasterBand(1).DataType,
        'prj':      srs_out.ExportToWkt(),
        'geotrans': (x_0, pixelsize, x_ang, y_0, y_ang, - pixelsize),
        'bandnum':  ds_in.RasterCount,
        'xsize':    newXcount,
        'ysize':    newYcount,
        'compress': 'DEFLATE',
    }
    # scroll(options)
    if ds_in.RasterCount>0:
        nodata = ds_in.GetRasterBand(1).GetNoDataValue()
        if nodata is not None:
            options['nodata'] = nodata
    ds_out = ds(path_out, options=options, editable=True)
    gdal.ReprojectImage(ds_in, ds_out, None, None, method)
    ds_out = None
    return 0

def repair_img(img_in, img_out, count, band_order=None, multiply = None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    # print(img_in, raster.GetGeoTransform(), '"', raster.GetProjection(), '"')
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':2, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    # print(img_out, new_raster.GetGeoTransform(), new_raster.GetProjection())
    for bin, bout in zip(band_order, range(1, count+1)):
        init_band = raster.GetRasterBand(bin)
        arr_ = init_band.ReadAsArray()
        init_nodata = init_band.GetNoDataValue()
        if init_nodata is None:
            init_nodata=0
            uniques, counts = np.unique(arr_, return_counts=True)
            total_sum = np.sum(counts)
            if counts[0]/total_sum>0.01:
                init_nodata=uniques[0]
            elif counts[-1]/total_sum>0.01:
                init_nodata=uniques[-1]
        arr_[arr_==init_nodata] = 0
        if multiply is not None:
            if bin in multiply.keys():
                arr_ = arr_ * multiply[bin]
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out

ms_folder = folder + 'MS_10m\\'
ms_ql_folder = folder + 'MS_30m\\'
ms_bands_folder = folder + 'BAND_10m\\'
ql_bands_folder = folder + 'BAND_30m\\'
for ms_file in folder_paths(ms_folder, 1, 'tif'):
    name = Name(ms_file)
    ql_file = fullpath(ms_ql_folder, '%s_%im' % (name, 30), 'tif')
    MakeQuicklook(ms_file, ql_file, epsg=None, pixelsize=30, method=gdal.GRA_Average, overwrite=False)
    for i, band in enumerate(['red', 'green', 'blue', 'nir']):
        repair_img(ms_file, fullpath(ms_bands_folder + band, '%s_%s' % (name, band), 'tif'), 1, band_order=[i + 1], multiply=None)
        repair_img(ql_file, fullpath(ql_bands_folder + band, '%s_%im_%s' % (name, 30, band), 'tif'), 1, band_order=[i + 1], multiply=None)
    print('Written MS QL: ' + name)
pan_folder = folder + 'PAN_2m\\'
pan_ql_folder = folder + 'PAN_30m\\'
for pan_file in folder_paths(pan_folder, 1, 'tif'):
    name = Name(pan_file)
    ql_file = fullpath(pan_ql_folder, '%s_%im' % (name, 30), 'tif')
    MakeQuicklook(pan_file, ql_file, epsg=None, pixelsize=30, method=gdal.GRA_Average, overwrite=False)
    print('Written PAN QL: ' + name)
