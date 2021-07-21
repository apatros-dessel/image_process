from geodata import *
from dotmap import DotMap

tile_step = 13860
tile_start_x = 139640
tile_start_y = 9993060
buffer = 420

tile_args_old = DotMap({
    'step': 13860,
    'start_x': 139640,
    'start_y': 9993060,
    'buffer': 420,
})

tile_args_new = DotMap({
    'step': 13860,
    'start_x': 139640,
    'start_y': 9993060,
    'buffer': 420,
})

tile_args_new = DotMap({
    'step':     138600,
    'start_x':  139640,
    'start_y':  9993060,
    'buffer':   4200,
    'x_min':    0,
    'x_max':    6,
    'y_min':    5,
    'y_max':    145,
})

tile_args_new_new = DotMap({
    'step':     69300,
    'start_x':  139640,
    'start_y':  9993060,
    'buffer':   2100,
    'x_min':    0,
    'x_max':    13,
    'y_min':    5,
    'y_max':    291,
    'x_len':    2,
    'y_len':    3,
})

tile_args_new = DotMap({
    'step': 138600,
    'start_x': 139640,
    'start_y': 9993060,
    'buffer': 4200,
})


def MakeTileWkt(row, col, p):
    x1 = p.start_x  + col * p.step          - p.buffer
    x2 = p.start_x  + (col + 1) * p.step    + p.buffer
    y1 = p.start_y  - row * p.step          - p.buffer
    y2 = p.start_y  - (row - 1) * p.step    + buffer
    wkt = 'MULTIPOLYGON ((( {0} {2}, {1} {2}, {1} {3}, {0} {3}, {0} {2} )))'.format(x1, x2, y1, y2)
    return wkt

def MakeTileZone(zone, path, south=False):
    json(path, srs = get_srs(4326))
    dout, lout = get_lyr_by_path(path, 1)
    lout.CreateField(ogr.FieldDefn('granule',4))
    defn = lout.GetLayerDefn()
    zone_geom = ZoneGeometry(zone, south)
    zone_srs = get_srs(32600+100*south+zone)
    for col in range(6, 46):
        for row in range(49, 900):
            wkt = MakeTileWkt(row, col)
            geom = ogr.CreateGeometryFromWkt(wkt, reference = zone_srs)
            geom.TransformTo(get_srs(4326))
            new_geom = changeXY(geom)
            if new_geom.Intersects(zone_geom):
                feat = ogr.Feature(defn)
                feat.SetGeometry(new_geom)
                feat.SetField('granule', str(zone*10**6+row*100+col))
                lout.CreateFeature(feat)
    dout = None

def ZoneGeometry(zone, south):
    x1 = zone * 6 - 186
    x2 = zone * 6 - 180
    y2 = (84,-84)[south]
    wkt = 'MULTIPOLYGON ((( {0} -84, {1} -84, {1} 84, {0} 84, {0} -84 )))'.format(x1, x2, y2)
    # wkt = 'MULTIPOLYGON ((( {0} 0, {1} 0, {1} {2}, {0} {2}, {0} 0 )))'.format(x1, x2, y2)
    geom = ogr.CreateGeometryFromWkt(wkt, reference=get_srs(4326))
    return geom

def MakeTile(path, p):
    json(path, srs = get_srs(4326))
    dout, lout = get_lyr_by_path(path, 1)
    lout.CreateField(ogr.FieldDefn('zone', 4))
    lout.CreateField(ogr.FieldDefn('granule',4))
    defn = lout.GetLayerDefn()
    # total = ogr.CreateGeometryFromWkt('MULTIPOLYGON ((( -180 -85, 180 -85, 180 85, -180 85, -180 -85 )))',
    # reference=get_srs(4326))
    for south in [0]:
        for zone in range(1,61):
            zone_geom = ZoneGeometry(zone, south)
            # feat = ogr.Feature(defn)
            # feat.SetGeometry(zone_geom)
            # lout.CreateFeature(feat)
            zone_srs = get_srs(32600 + 100 * south + zone)
            # print(32600 + 100 * south + zone)
            for col in range(p.x_min, p.x_max):
                for row in range(p.y_min, p.y_max):
                    # wkt = MakeTileWkt(row, col)
                    wkt = MakeTileWkt(row, col, p)
                    geom = ogr.CreateGeometryFromWkt(wkt, reference = zone_srs)
                    geom.TransformTo(get_srs(4326))
                    # print(geom.ExportToWkt())
                    new_geom = changeXY(geom)
                    # print(geom.ExportToWkt(), new_geom.ExportToWkt())
                    if new_geom.Intersects(zone_geom):
                    # if True:
                        if zone<10:
                            new_geom = ControlLimits(new_geom, 0)
                        elif zone>51:
                            new_geom = ControlLimits(new_geom, 1)
                        feat = ogr.Feature(defn)
                        feat.SetGeometry(new_geom)
                        feat.SetField('zone', str(zone))
                        feat.SetField('granule', str(zone*10**(p.x_len+p.y_len)+row*10**p.x_len+col))
                        lout.CreateFeature(feat)
            print('FINISHED ZONE %i' % zone)
    # feat = ogr.Feature(defn)
    # feat.SetGeometry(total)
    # lout.CreateFeature(feat)
    dout = None

def ControlLimits(geom, right):
    coords = geom.ExportToWkt().split(',')
    for i, coord in enumerate(coords):
        search = re.search(r'-?\d+\.?\d* -?\d+\.?\d*', coord)
        if search is not None:
            vals = search.group()
            new_vals = vals.split(' ')
            if right:
                if new_vals[0][0]=='-':
                    new_vals[0] = '180'
                else:
                    continue
            elif new_vals[0][0]=='1':
                new_vals[0] = '-180'
            else:
                continue
            new_vals = ' '.join(new_vals)
            coords[i] = coord.replace(vals, new_vals)
        else:
            print('UNABLE TO CHECK COORDS: %s' % coord)
    new_geom = ogr.Geometry(wkt = ','.join(coords))
    return new_geom



# MakeTileZone(37, r'e:\rks\new_tiles_s%i.json' % 37, south=1)
MakeTile(r'e:\rks\new_tiles_pan_geoton.json', tile_args_new_new)

sys.exit()
din, lin = get_lyr_by_path(r'e:\rks\tiles_rus.geojson')
report = OrderedDict()
for feat in lin:
    grn = feat.GetField('granule')
    if grn:
        values = OrderedDict()
        values['zone'] = int(grn[:-6])
        values['col'] = int(grn[-6:-2])
        values['row'] = int(grn[-2:])
        wkt = feat.GetGeometryRef().ExportToWkt()
        points = wkt.split(',')
        for i, point in enumerate(points):
            s = re.search(r'\d+\.?\d* \d+\.?\d*', point)
            if s:
                xy = flist(s.group().split(' '), float)
                xy = flist(xy, int)
                values['x%i' % i] = xy[0]
                values['y%i' % i] = xy[1]
            else:
                print(point)
        report[grn] = values
# scroll(report)
# sys.exit()
dict_to_xls(r'e:\rks\tiles_rus.xls', report, col_list=['','zone','row','col',
                                                             'x0','x1','x2','x3','x4',
                                                             'y0','y1','y2','y3','y4'])