from geodata import *

# Записать растр снимка в установленном формате
def repair_img(img_in, img_out, count, band_order=None, multiply = None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    print(img_in, raster.GetGeoTransform(), '"', raster.GetProjection(), '"')
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':3, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    print(img_out, new_raster.GetGeoTransform(), new_raster.GetProjection())
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

def SavePointsToMultipolygon(path, points_list, srs=None):
    json(path, srs = srs)
    dout, lout = get_lyr_by_path(path, 1)
    feat_defn = lout.GetLayerDefn()
    feat = ogr.Feature(feat_defn)
    geom = MultipolygonFromList(points_list, srs = None)
    feat.SetGeometry(geom)
    lout.CreateFeature(feat)
    dout = None

def SavePoints(path, points_list, srs=None):
    json(path, srs = srs)
    dout, lout = get_lyr_by_path(path, 1)
    lout.CreateField(ogr.FieldDefn('X', 2))
    lout.CreateField(ogr.FieldDefn('Y', 2))
    feat_defn = lout.GetLayerDefn()
    for coords in points_list:
        feat = ogr.Feature(feat_defn)
        wkt = 'POINT (%f %f)' % (coords[:2])
        geom = ogr.CreateGeometryFromWkt(wkt)
        feat.SetGeometry(geom)
        feat.SetField('X', coords[0])
        feat.SetField('Y', coords[1])
        lout.CreateFeature(feat)
    dout = None


file = r'e:\rks\razmetka_source\kanopus_ms_strips\img_strips\KV1_01644_00457_00_KANOPUS_20121107_091940_092014.MS.RS.tif'
raster = gdal.Open(file)
gcp = raster.GetGCPs()
extent = GetExtentFromGCP(gcp)
# SavePointsToMultipolygon(file.replace('.tif','.json'), extent, srs=get_srs(4326))
SavePoints(file.replace('.tif','_points.json'), extent, srs=get_srs(4326))
print(extent)
sys.exit()
repair_img(file, file.replace('.tif','_new.tif'), 4)