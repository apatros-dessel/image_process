from geodata import *
from image_processor import process

pin = r'd:\digital_earth\Niznii_Tagil\Нижний Тагил 2019.shp'
folder_out = r'd:\digital_earth\Niznii_Tagil\2019'
make_cover = True

def copy_file(file_in, file_out, id='<file>'):
    if os.path.exists(file_out):
        print('FILE EXISTS: %s' % id)
    else:
        suredir(os.path.dirname(file_out))
        shutil.copyfile(file_in, file_out)
        print('FILE WRITTEN: %s' % id)

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
    lyr_out.CreateField(ogr.FieldDefn('satid', 4))
    feat_defn = lyr_out.GetLayerDefn()
    for file in files:
        ds_ = gdal.Open(file)
        if ds_:
            f,id,e = split3(file)
            feat = ogr.Feature(feat_defn)
            feat.SetField('id', id)
            geom = RasterGeometry(ds_, reference=srs)
            # print(geom.ExportToWkt())
            feat.SetGeometry(geom)
            proc = process().input(f)
            ascene = proc.scenes[0]
            if ascene:
                satid = ascene.meta.sat
                feat.SetField('satid', satid)
            lyr_out.CreateFeature(feat)
    ds_out = None

din, lin = get_lyr_by_path(pin)
result = []

if lin:
    suredir(folder_out)
    for feat in lin:
        id = feat.GetField('id')
        path = feat.GetField('path')
        if path:
            folder, meta = os.path.split(path)
            files = folder_paths(folder,1,'tif')
            if files:
                for file in files:
                    f,n,e = split3(file)
                    new_file = fullpath(folder_out, n, e)
                    # copy_file(file, new_file, id)
                    if make_cover:
                        if not os.path.exists(new_file):
                            result.append(file)
cover_id = split3(pin)[1]
TotalCover(fullpath(folder_out, cover_id, 'json'), result, srs = None)