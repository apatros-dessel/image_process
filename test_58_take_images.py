from geodata import *
from image_processor import process

pin = [
    # r'\\172.21.195.2\FTP-Share\ftp',
    # r'd:\digital_earth',
    # r'e:\resursp_filtered',
    # r'e:\rks',
    # r'e:\20200713_kanopus',
    # r'\\tt-pc-10-quadro\FTP_Share14TB\S3',
    r'\\172.21.195.215\thematic\14T_all\S3'
]
id_list_txt = r'd:\rks\KV_krasnoyarsk_TBO\scene_ids.txt'
name_tmpt = r'KV.+_P?S?S\d?_.*[LNB0-9]$'#r'RP.+[LNB0-9]$'
cover_vector_path = None# r'\\172.21.195.2/FTP-Share/ftp/!FINAL_PRODUCTS/1.Эко-мониторинг/Э1Б.Исходная ситуация - официальные полигоны складирования отходов/Э1Б.Свердловская/tbo_sverdlovskay_poligon.shp'#D:/digital_earth/RSP_Tatarstan/Tatarstan_objects.shp
pout = r'd:\rks\KV_krasnoyarsk_TBO'
target = 'LIST COPY PATHS'
target = 'COPY RASTER'
file_paths = r'\\172.21.195.215\thematic\14T_all\S3\tif.txt'
search_for_vector_cover = True

def raster_geom(ds, reference=None):
    if ds is None:
        print('ERROR: DS IS NONE')
        return None
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

def json_geom(json_path, reference=None):
    jds, jlyr = get_lyr_by_path(json_path)
    if jlyr:
        feat = jlyr.GetNextFeature()
        if feat:
            new_cover_geom = feat.GetGeometryRef()
            if new_cover_geom:
                geom = new_cover_geom
                new_cover_srs = jlyr.GetSpatialReference()
                if new_cover_srs:
                    if new_cover_srs != reference:
                        coordTrans = osr.CoordinateTransformation(new_cover_srs, reference)
                        geom.Transform(coordTrans)
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
        new_files = folder_paths(dir_in,1,'tif')
        if new_files:
            files.extend(new_files)
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

# scroll(files)
# scroll(id_list)
scene_folders = []
suredir(pout)

for file in files:
    f,n,e = split3(file)
    if name_tmpt:
        if not re.search(name_tmpt, n):
            continue
    # print(file)
    if id_list_txt:
        for id in id_list:
            if re.search(id, n):
                copy_file(file_in, fullpath(pout,n,e), id=n)
                if not f in scene_folders:
                    scene_folders.append(f)
    if cover_vector_path:
        ds_cover, lyr_cover = get_lyr_by_path(cover_vector_path)
        if lyr_cover:
            srs = lyr_cover.GetSpatialRef()
            if search_for_vector_cover:
                json_paths = folder_paths(f,1,'json')
                if json_paths:
                    for json_ in json_paths:
                        jf, jn, j = split3(json_)
                        if re.search(name_tmpt, jn):
                            raster_geometry = json_geom(json_, reference=srs)
                            if raster_geometry:
                                break
            else:
                raster_geometry = None
            if raster_geometry is None:
                raster_geometry = raster_geom(gdal.Open(file), reference=srs)
            if raster_geometry is None:
                print('UNABLE TO EXTRACT GEOMETRY FROM: %s' % n)
                continue
            for feat in lyr_cover:
                vector_geometry = feat.GetGeometryRef()
                # print('r: '+raster_geometry.ExportToWkt()[:50])
                # print('v: '+vector_geometry.ExportToWkt()[:50])
                if raster_geometry.Intersects(vector_geometry):
                    print('MATCH: %s' % n)
                    if copy_:
                        copy_file(file, fullpath(pout, n, e), id=n)
                    else:
                        copy_paths.append(file)
                    if not f in scene_folders:
                        scene_folders.append(f)
                    break

if target=='LIST COPY PATHS':
    if len(copy_paths) > 0:
        with open(fullpath(pout, 'copy_paths.txt'), 'w') as txt:
            txt.write('\n'.join(copy_paths))
        try:
            proc = process().input(scene_folders, imsys_list=['RSP'])
            proc.GetCoverJSON(fullpath(pout, 'vector_cover.json'))
        except:
            print('ERROR CREATING VECTOR COVER')
