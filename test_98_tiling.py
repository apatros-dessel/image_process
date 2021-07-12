from geodata import *

pin = r'e:\test\bands\basic'
pout = r'e:\test\bands\tiles'
# iout = r'e:\test\basic'
suredir(pout)
tile_source = r'\\172.21.195.2\thematic\Sadkov_SA\tiles_gshmsa.json'

def crop_bigraster_gdal(path_in, path_vec, path_out):
    command = "gdalwarp -of GTiff -cutline {path_vec} -crop_to_cutline -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 {path_in} {path_out} -co NUM_THREADS=ALL_CPUS".format(path_vec=path_vec, path_in=path_in, path_out=path_out)
    os.system(command)
    if RasterDataArea(path_out) == 0:
        delete(path_out)
    else:
        StripRaster(path_out, compress='DEFLATE')

def image_area(ifile, ofile, srs=None):
    ds_ = gdal.Open ( ifile )
    width = ds_.RasterXSize
    height = ds_.RasterYSize
    gt = ds_.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]
    template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
    wkt = template % r1
    geom = ogr.CreateGeometryFromWkt(wkt, reference = get_srs(ds_))
    if srs is None:
        srs = get_srs(ds_)
    else:
        srs = get_srs(srs)
        if srs != get_srs(ds_):
            geom.TransformTo(get_srs(4326))
            geom = changeXY(geom)
    # print(srs.ExportToWkt(), geom.ExportToWkt())
    json(ofile, srs = srs)
    dout, lout = get_lyr_by_path(ofile, 1)
    defn = lout.GetLayerDefn()
    feat = ogr.Feature(defn)
    feat.SetGeometry(geom)
    lout.CreateFeature(feat)
    dout = None
    return None

td, tl = get_lyr_by_path(tile_source)

for file in folder_paths(pin,1,'tif'):
    name = Name(file)
    # ifile = fullpath(iout, name, 'tif')
    if FindAny(name, ['_red', 'green', '_blue', '_nir', '_nir1', '_nir2'], False):
        parts = name.split('_')
        id = '_'.join(parts[:-1])
        color = '_' + parts[-1]
    else:
        id = name
        color = ''
    ofile = tempname('json')
    image_area(file, ofile, srs=get_srs(4326))
    dar,lar = get_lyr_by_path(ofile)
    far = lar.GetNextFeature()
    gar = far.GetGeometryRef()
    print(gar.ExportToWkt())
    # sys.exit()
    tl.ResetReading()
    for tf in tl:
        grn = tf.GetField('granule')
        # grn_name = '%s.GRN%s' % (name, grn)
        grn_name = '%s.GRN%s%s' % (id, grn, color)
        grn_file = fullpath(pout, grn_name, 'tif')
        if os.path.exists(grn_file):
            continue
        tg = tf.GetGeometryRef()
        if tg.Intersects(gar):
            path_vec = filter_dataset_by_col(tile_source, 'granule', grn, path_out=tempname('json'))
            crop_bigraster_gdal(file, path_vec, grn_file)
            print('WRITTEN: %s' % grn_name)
        else:
            print('WROHG: %s' % grn)
            pass
