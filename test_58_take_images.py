from geodata import *

pin = [
    r'\\172.21.195.2\FTP-Share\ftp',
    r'd:\digital_earth',
    r'e:\resursp_filtered',
    r'e:\rks',
    r'F:\102_2020_108_RP',
]
id_list_txt = None # r'e:\rks\s3\kanopus_pms\names_TBO_krasnoyarsk.txt'
name_tmpt = r'RP.+[NB0-9]$'
cover_vector_path = r'\\172.21.195.2\FTP-Share\ftp\!region_shows\krym\Эко\Свалки\KRYM_SIMFEROPOLSKIY_border.shp'#tbo_krym_narusheniya.shp#tbo_krym_poligon
pout = r'd:\digital_earth\RSP_Simferopol'
target = 'LIST COPY PATHS'
# target = 'COPY RASTER'
file_paths = r'd:\digital_earth\RSP_Simferopol\file_list.txt'

def raster_geom(ds, reference=None):
    width = ds.RasterXSize
    height = ds.RasterYSize
    srs = osr.SpatialReference()
    proj = ds.GetProjection()
    if proj=='':
        print('ERROR: CANNOT GET PROJECTION')
        return None
    srs.ImportFromWkt(proj)
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    # if sys.version.startswith('2'):
        # template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    # else:
        # template = 'POLYGON ((%(miny)f %(minx)f, %(miny)f %(maxx)f, %(maxy)f %(maxx)f, %(maxy)f %(minx)f, %(miny)f %(minx)f))'
    r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
    wkt = template % r1
    if sys.version.startswith('2'):
        geom = ogr.Geometry(wkt=wkt)
    else:
        geom = ogr.CreateGeometryFromWkt(wkt, srs)
    if srs!=reference:
        coordTrans = osr.CoordinateTransformation(srs, reference)
        geom.Transform(coordTrans)
        # if sys.version.startswith('3'):
            # geom = changeXY(geom)
    return geom

def copy_file(file_in, file_out, id='<file>'):
    if os.path.exists(file_out):
        print('FILE EXISTS: %s' % id)
    else:
        suredir(os.path.dirname(file_out))
        shutil.copyfile(file_in, file_out)
        print('FILE WRITTEN: %s' % id)

if os.path.exists(file_paths):
    files = open(file_paths).read().split('\n')
else:
    pin = obj2list(pin)
    files = []
    for dir_in in pin:
        files.extend(folder_paths(dir_in,1,'tif'))
    if id_list_txt:
        id_list = open(id_list_txt).read().split('\n')
    with open(file_paths, 'w') as txt:
        txt.write('\n'.join(files))

if target=='LIST COPY PATHS':
    copy_paths = []
    copy_ = False
elif target=='COPY RASTER':
    copy_ = True
else:
    print('Unreckognized target: need "LIST COPY PATHS" or "COPY RASTER"')

scroll(files)
# scroll(id_list)

for file in files:
    f,n,e = split3(file)
    if name_tmpt:
        if not re.search(name_tmpt, n):
            continue
    print(file)
    if id_list_txt:
        for id in id_list:
            if re.search(id, n):
                copy_file(file_in, fullpath(pout,n,e), id=n)
    if cover_vector_path:
        ds_cover, lyr_cover = get_lyr_by_path(cover_vector_path)
        if lyr_cover:
            srs = lyr_cover.GetSpatialRef()
            raster_geometry = raster_geom(gdal.Open(file), reference=srs)
            if raster_geometry is None:
                print('UNABLE TO EXTRACT GEOMETRY FROM: %s' % n)
                continue
            for feat in lyr_cover:
                vector_geometry = feat.GetGeometryRef()
                # print('r: '+raster_geometry.ExportToWkt()[:50])
                # print('v: '+vector_geometry.ExportToWkt()[:50])
                if raster_geometry.Intersects(vector_geometry):
                    if copy_:
                        copy_file(file, fullpath(pout, n, e), id=n)
                    else:
                        copy_paths.append(file)
                    break

if target=='LIST COPY PATHS':
    if len(copy_paths) > 0:
        suredir(pout)
        with open(fullpath(pout, 'copy_paths.txt'), 'w') as txt:
            txt.write('\n'.join(copy_paths))
