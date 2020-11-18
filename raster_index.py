from geodata import *
from image_processor import process

folders = [
    # r'e:\\',
    # r'\\172.21.195.2\FTP-Share\ftp',
    # r'd:\\',
]

def RasterGeometry(ds_, reference=None):
    width = ds_.RasterXSize
    height = ds_.RasterYSize
    gt = ds_.GetGeoTransform()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds_.GetProjection())
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
    wkt = template % r1
    if sys.version.startswith('2'):
        geom = ogr.Geometry(wkt=wkt)
    else:
        geom = ogr.CreateGeometryFromWkt(wkt, reference)
    if srs!=reference:
        trans = osr.CoordinateTransformation(srs, reference)
        geom.Transform(trans)
        if sys.version.startswith('3'):
            geom = changeXY(geom)
    return geom

def TotalCover(pout, files, srs = None):
    driver = ogr.GetDriverByName('GeoJSON')
    ds_out = driver.CreateDataSource(pout)
    if srs is None:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
    lyr_out = ds_out.CreateLayer('', srs, ogr.wkbMultiPolygon)
    lyr_out.CreateField(ogr.FieldDefn('id', 4))
    lyr_out.CreateField(ogr.FieldDefn('path', 4))
    lyr_out.CreateField(ogr.FieldDefn('satid', 4))
    lyr_out.CreateField(ogr.FieldDefn('geomerror', 8))
    feat_defn = lyr_out.GetLayerDefn()
    i = 0
    for file in files:
        try:
            ds_ = gdal.Open(file)
        except:
            ds_ = None
        if ds_:
            i += 1
            f,id,e = split3(file)
            feat = ogr.Feature(feat_defn)
            feat.SetField('id', id)
            feat.SetField('path', file)
            try:
                proc = process().input(f)
                if len(proc)==1:
                    ascene = proc.scenes[0]
                    satid = ascene.meta.sat
                    feat.SetField('satid', satid)
            except:
                feat.SetField('satid', None)
            try:
                geom = RasterGeometry(ds_, reference=srs)
                feat.SetGeometry(geom)
                feat.SetField('geomerror', False)
            except:
                feat.SetField('geomerror', True)
            lyr_out.CreateFeature(feat)
    ds_out = None
    return i

def IndexFolder(folder, index_name, types=None, timelag=None):
    endpath = fullpath(folder, index_name, 'txt')
    if os.path.exists(endpath):
        try:
            time_old, strfiles = open(endpath).read().split('\n\n')
            time_old = datetime.strptime(time_old, '%Y-%m-%d %H:%M:%S.%f')
            if timelag:
                if datetime.now() - time_old < timelag:
                    return strfiles.split('\n')
        except:
            pass
    time_start = str(datetime.now())
    files = folder_paths(folder,1,types,filter_folder=['$RECYCLE.BIN', '__shelter'])
    with open(endpath, 'w') as txt:
        txt.write('%s\n\n%s' % (time_start, '\n'.join(files)))
    return files

def CoverTIF(folder, index_name = 'IndexTIF'):
    files = IndexFolder(folder, index_name, 'tif')
    count = TotalCover(fullpath(folder, index_name, 'json'), files, srs=None)
    print('CREATED COVER OF %i FILES IN %s' % (count, folder))

for folder in folders:
    CoverTIF(folder)
