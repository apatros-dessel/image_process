# -*- coding: utf-8 -*-

# FINDS THE NEAREST POINTS IN TWO SHAPEFILES AND ATTACHES THE ATTRIBUTES OF ONE LAYER'S NEAREST POINT TO THE OTHERS'
# Was originaly made to attach topomap heights labels to the height points

from min_dist import *
import datetime as dtime
'''
path = 'c:\\sadkov\\forest\\dem'
file_points = r'relief_points_severnoye.shp'
file_labels = r'relief_labels_severnoye.shp'
'''
path = r'C:\sadkov\topo\Relief_rus_WGS84'
file_points = r'27_Relief_points.shp'
file_labels = r'27_Relief_labels.shp'

t = dtime.datetime.now()
points_ds = ogr.Open('{}\\{}'.format(path, file_points))
labels_ds = ogr.Open('{}\\{}'.format(path, file_labels))
#lyr = ds.GetLayer()

points = lyr2dict(points_ds.GetLayer(), ['new_id', 'X_WGS84', 'Y_WGS84', 'type'])
points = filter_by_attr(points, 'type', val='СКАЛЫ-ОСТАНЦЫ')
labels = lyr2dict(labels_ds.GetLayer(), ['new_id', 'X_WGS84', 'Y_WGS84', 'height'])

t = dtime.datetime.now()
result = get_nearest(points, labels, x_col='X_WGS84', y_col='Y_WGS84', id_col='new_id', h_col='height')
print(dtime.datetime.now()-t)

result2 = filter_by_distance(result, id_col='new_id', h_col='height', del_empty_vals=True)
#result2['Height'] = result2.pop('height')


fields2export = {
    'new_id': ogr.OFTInteger,
    'X_WGS84': ogr.OFTReal,
    'Y_WGS84': ogr.OFTReal,
    'height': ogr.OFTInteger,
    'names_id': ogr.OFTInteger,
    'type': ogr.OFTString,
    'dist': ogr.OFTReal,
}
dict2shp(r'c:\sadkov\forest\euron\dem\relief_points.shp', result2, fields2export, epsg=32653, x_coord='X_WGS84', y_coord='Y_WGS84')

print(dtime.datetime.now()-t)
