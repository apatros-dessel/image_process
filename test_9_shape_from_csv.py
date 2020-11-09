# -*- coding: utf-8 -*-

# Makes shapefiles from csv coordinate files

import os
import csv
import ogr
import osr
import re

lat_sign = {'N': 1, 'S': -1, 'С': 1, 'Ю': -1}
lon_sign = {'W': -1, 'E': 1, 'З': -1, 'В': 1}
dir_dict = {'lat': lat_sign, 'lon': lon_sign}
dir_symb_list = {'lat': list(globals()['lat_sign'].keys()),
                     'lon': list(globals()['lon_sign'].keys())}

def csv2dict(path, names1st_line=True, delimeter=';'):
    if not os.path.exists(path):
        raise Exception('Path not found %s' % path)
    csvfile = csv.reader(open(path))
    read_list = []
    for line in csvfile:
        read_list.append(line[0].split(delimeter))
    len_ = len(read_list[0])
    for line_list in read_list:
        #print(line_list)
        if len(line_list) != len_:
            raise Exception(r"Number of columns doesn't match")
    if names1st_line:
        names_list = read_list[0]
        read_list = read_list[1:]
    else:
        names_list = []
        for num in range(len_):
            names_list.append('col_{}'.format(num))
    csvdata = {}
    for num in range(len_):
        if names_list[num] in csvdata:
            col_name = '{}_2'.format(names_list[num])
            copy_num = 2
            while col_name in csvdata:
                copy_num += 1
                col_name = '{}_{}'.format(names_list[num], copy_num)
        else:
            col_name = names_list[num]
        csvdata[col_name] = get_val(read_list, num)
    return csvdata

def get_val(read_list, id):
    export = []
    for line in read_list:
        try:
            export.append(line[id])
        except:
            export.append(None)
    return export

def coord_sign(coord_symb):
    dir_dict = globals()['dir_dict']
    for sign_list in dir_dict:
        if coord_symb in dir_dict[sign_list]:
            return {str(sign_list): dir_dict[sign_list][coord_symb]}
    print('No sign marker identified')
    return None

def split_coords(coord_str, symb):
    dir_symb_list = globals()['dir_symb_list']
    coord_str_full = dir_symb_list['lat'] + dir_symb_list['lon']
    for sign_list in dir_symb_list:
        if symb in dir_symb_list[sign_list]:
            search_result = re.search(r'[{}][^{}+'.format(symb, str(coord_str_full)[1:]), coord_str)
            if search_result is not None:
                return search_result.group()
    print('No coordinates found for: {}'.format([coord_str, symb]))
    return None

def parse_coordinate(coord_str):
    dir_symb_list = globals()['dir_symb_list']
    direct_dict = {'lat': 1, 'lon': 1}
    coord_dict = {'lat': (0,0,0), 'lon': (0,0,0)}
    for coord_list in dir_symb_list:
        for coord_sign_symb in dir_symb_list[coord_list]:
            if coord_sign_symb in coord_str:
                sign_dict = coord_sign(coord_sign_symb)
                if sign_dict is not None:
                    direct_dict.update(coord_sign(coord_sign_symb))
                coord_str_part = split_coords(coord_str, coord_sign_symb)
                search_result = re.search(r'\d{2,3}\D+\d{2}\D+\d+', coord_str_part)
                if search_result is not None:
                    search_result = search_result.group()
                    deg = direct_dict[coord_list]*int(re.search('\d+', search_result).group())
                    min = direct_dict[coord_list]*int(re.search('\d{2}', search_result[2:]).group())
                    sec = direct_dict[coord_list]*int(re.search('\d{2,}', search_result[4:]).group())
                    coord_dict.update({coord_list: (deg, min, sec)})
    return coord_dict

def dms2dd(coord_dict, method='deg_min_sec'):
    dd_dict = {'lat': 0.0, 'lon': 0.0}
    for direct in dd_dict.keys():
        if method=='deg_min_sec':
            dd_dict[direct] = float(coord_dict[direct][0]) + float(coord_dict[direct][1]) / 60 + float(coord_dict[direct][2]) / 3600
        elif method=='deg_min_decmin':
            dd_dict[direct] = float(coord_dict[direct][0]) + (float(coord_dict[direct][1]) + float(coord_dict[direct][2]) / float(10**len(str(int(coord_dict[direct][2]))))) / 60
        else:
            print('Unreckognized method: "{}"'.format(method))
    return dd_dict

def dd2shp(path, coord_dict_list, epsg=4326, shptype='point'):
    type_dict = {
        'point': ogr.wkbPoint,
        'polyline': ogr.wkbLineString,
        'polygon': ogr.wkbPolygon,
    }
    if shptype not in type_dict:
        print('Cannot reckognize type: %type_dict')
        return None
    else:
        shptype = type_dict[shptype]
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(path):
        driver.DeleteDataSource(path)
    ds = driver.CreateDataSource(path)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    lyr = ds.CreateLayer('obj_from_coords', srs, shptype)

    if shptype == ogr.wkbPoint:
        for coord_dict in coord_dict_list:
            feat = ogr.Feature(lyr.GetLayerDefn())
            wkt = "POINT (%f %f)" % (float(coord_dict['lon']), float(coord_dict['lat']))
            point = ogr.CreateGeometryFromWkt(wkt)
            feat.SetGeometry(point)
            lyr.CreateFeature(feat)
            feat = None

    elif shptype == ogr.wkbLineString:
        feat = ogr.Feature(lyr.GetLayerDefn())
        wkt = "LINESTRING ("
        for coord_dict in coord_dict_list:
            wkt += "%f %f, " % (float(coord_dict['lon']), float(coord_dict['lat']))
        wkt = wkt[:-2] + ")"
        polyline = ogr.CreateGeometryFromWkt(wkt)
        feat.SetGeometry(polyline)
        lyr.CreateFeature(feat)
        feat = None

    elif shptype == ogr.wkbPolygon:
        feat = ogr.Feature(lyr.GetLayerDefn())
        wkt = "POLYGON (("
        for coord_dict in coord_dict_list:
            wkt += "%f %f, " % (float(coord_dict['lon']), float(coord_dict['lat']))
        if coord_dict_list[0] != coord_dict_list[-1]:
            wkt += "%f %f, " % (float(coord_dict_list[0]['lon']), float(coord_dict_list[0]['lat']))
        wkt = wkt[:-2] + "))"
        polygon = ogr.CreateGeometryFromWkt(wkt)
        feat.SetGeometry(polygon)
        lyr.CreateFeature(feat)
        feat = None

    else:
        print('Cannot reckognize type: %type_dict')

    return None
'''
x = 'N57.56.43532E36.23.56723'
y = dms2dd(parse_coordinate(x), method='deg_min_decmin')
print(y)
dd2shp(r'C:\sadkov\test.shp', [y])
'''

def csv2shp(csv_path, shp_path, delimeter=';', col_names=None, coord_source='DMS', coord_method='deg_min_sec', shptype='point'):
    csv_dict = csv2dict(csv_path, delimeter=delimeter)
    coords_list=[]
    if col_names is None:
        col_names = {
            'id': 'id',
            'dec_x': 'DEC_X',
            'x_dd': 'X_DD',
            'x_mm': 'X_MM',
            'x_ss': 'X_SS',
            'dec_y': 'DEC_Y',
            'y_dd': 'Y_DD',
            'y_mm': 'Y_MM',
            'y_ss': 'Y_SS',
            'shpid': 'shpid',
        }
    for id in range(len(csv_dict['id'])):
        try:
            if coord_source == 'DEC_DD':
                if int(csv_dict[col_names['y_dd']][id]) < 90:
                    coords_list.append({
                        'id': csv_dict[col_names['id']][id],
                        'lat': csv_dict[col_names['y_dd']][id],
                        'lon': csv_dict[col_names['x_dd']][id],
                    })
                else:
                    coords_list.append({
                        'id': csv_dict[col_names['id']][id],
                        'lat': csv_dict[col_names['x_dd']][id],
                        'lon': csv_dict[col_names['y_dd']][id],
                    })
            elif coord_source == 'DMS':
                if int(csv_dict[col_names['y_dd']][id]) < 90:
                    dms = {'lat': (int(csv_dict[col_names['y_dd']][id]),
                                   int(csv_dict[col_names['y_mm']][id]),
                                   float(csv_dict[col_names['y_ss']][id])),
                           'lon': (int(csv_dict[col_names['x_dd']][id]),
                                   int(csv_dict[col_names['x_mm']][id]),
                                   float(csv_dict[col_names['x_ss']][id])),
                           }
                else:
                    dms = {'lon': (int(csv_dict[col_names['y_dd']][id]),
                                   int(csv_dict[col_names['y_mm']][id]),
                                   float(csv_dict[col_names['y_ss']][id])),
                           'lat': (int(csv_dict[col_names['x_dd']][id]),
                                   int(csv_dict[col_names['x_mm']][id]),
                                   float(csv_dict[col_names['x_ss']][id])),
                           }
                dd = dms2dd(dms, method=coord_method)
                dd['id'] = int(csv_dict[col_names['id']][id])
                coords_list.append(dd)
        except:
            print('Cannot add coodrinates %i' % id)
        #print(coords_list[id])
    dd2shp(shp_path, coords_list, shptype=shptype)
    return True

csv_dir = r'e:\temp'
shp_dir = r'e:\temp'
dir_list = os.listdir(csv_dir)
csv_list = []
for csv_path in dir_list:
    if csv_path.endswith('.csv'):
        csv_list.append(csv_path)
#csv_list=[r'C:\sadkov\forest\lesopatolog\new_rita\62-34-14-17.csv']
os.chdir(csv_dir)
for path in csv_list:
    csv_name = os.path.splitext(os.path.split(path)[1])[0]
    shp_path = '{}\{}.shp'.format(shp_dir, csv_name)
    csv2shp(path, shp_path, shptype='polygon')
    try:
        csv2shp(path, shp_path, shptype='polygon')
        print('Written %s' % shp_path)
    except:
        #print('Cannot write %s' % shp_path)
        #print(path, csv2dict(path))
        pass