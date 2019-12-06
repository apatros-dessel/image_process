# -*- coding: utf-8 -*-

# Unites all shapefiles with icesat data

from min_dist import *
import os
import datetime as dtime

path = r'C:\sadkov\forest\icesat\new'
file_points_list = ['20181106.shp',
 '20181117.shp',
 '20181121.shp',
 '20181125.shp',
 '20181209.shp',
 '20181220.shp',
 '20181224.shp',
 '20181228.shp',
 '20190103.shp',
 '20190107.shp',
 '20190118.shp',
 '20190122.shp',
 '20190126.shp',
 '20190205.shp',
 '20190209.shp',
 '20190216.shp',
 '20190220.shp',]
fin_file = 'icesat_points.shp'

os.chdir(path)
['segment_id', 'longitude', 'latitude', 'h_li', 'beam', 'file_name']
dict_all = {'segment_id': [],
            'longitude': [],
            'latitude': [],
            'h_li': [],
            'beam': [],
            'file_name': []}
dict_format = {'segment_id': int,
            'longitude': float,
            'latitude': float,
            'h_li': float,
            'beam': str,
            'file_name': str}

for file_points in file_points_list:
    points_ds = ogr.Open('{}\\{}'.format(path, file_points))
    points = lyr2dict(points_ds.GetLayer(), ['segment_id', 'longitude', 'latitude', 'h_li', 'beam', 'file_name'])
    for key in points:
        dict_all[key] += list(points[key])

for key in ['segment_id', 'longitude', 'latitude', 'h_li', 'beam', 'file_name']:
    if dict_format[key] in [int, float]:
        for id in range(len(dict_all[key])):
            try:
                if dict_all[key][id] is None:
                    dict_all[key][id] = 0
                else:
                    dict_all[key][id] = float(dict_all[key][id])
            except:
                print(key, dict_all[key][id])
                raise Exception
    dict_all[key] = np.array(dict_all[key]).astype(dict_format[key])

fields2export = {
    'segment_id': ogr.OFTInteger,
    'latitude': ogr.OFTReal,
    'longitude': ogr.OFTReal,
    'h_li': ogr.OFTReal,
    'beam': ogr.OFTString,
    'file_name': ogr.OFTString,
}
dict2shp(fin_file, dict_all, fields2export, epsg=4326, x_coord='longitude', y_coord='latitude')

#print(dtime.datetime.now()-t)