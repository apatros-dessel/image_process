# -*- coding: utf-8 -*-

# Calculates differenses between two radar elevation values to get forest height

from min_dist import *
import datetime as dtime
'''
path = 'c:\\sadkov\\forest\\dem'
file_points = r'relief_points_severnoye.shp'
file_labels = r'relief_labels_severnoye.shp'
'''

def height_from_points(points, beam_attr='beam', segment_attr='segment_id', file_attr='file_name', x_attr='longitude', y_attr='latitude', elev_attr='h_li', take_canopy_coords=False):
    heights = {
        segment_attr: [],
        file_attr: [],
        x_attr: [],
        y_attr: [],
        'height': [],
    }
    beams = [['gt1r', 'gt1l'], ['gt2r', 'gt2l'], ['gt3r', 'gt3l']]
    filename_list = []
    file_index = []
    for id in range(len(points[file_attr])):
        filenames = points[file_attr]
        if points[file_attr][id] in filename_list:
            filename_list.append(points[file_attr][id])
            file_index.append(len(filename_list))
        else:
            file_index.append(filename_list.index(points[file_attr][id]))
    file_index = np.array(file_index)
    for beam in beams:
        for id in range(len(points[beam_attr])):
            if points[beam_attr][id] == beam[0] and points[elev_attr][id] not in [None, 0]:
                for id2 in range(len(points[beam_attr])):
                    if (points[beam_attr][id2] == beam[1] and points[segment_attr][id2] == points[segment_attr][id])\
                            and ((file_index[id2] == file_index[id]) and (points[elev_attr][id2] not in [None, 0])):
                        heights[segment_attr].append(points[segment_attr][id2])
                        heights[file_attr].append(points[file_attr][id2])
                        heights['height'].append(float(points[elev_attr][id2]) - float(points[elev_attr][id]))
                        if take_canopy_coords:
                            heights[x_attr].append(points[x_attr][id2])
                            heights[y_attr].append(points[y_attr][id2])
                        else:
                            heights[x_attr].append(points[x_attr][id])
                            heights[y_attr].append(points[y_attr][id])
    return heights



path = r'C:\sadkov\forest\icesat\new'
file_points = r'icesat_points_aoi.shp'
#file_labels = r'euron_labels.shp'

t = dtime.datetime.now()
points_ds = ogr.Open('{}\\{}'.format(path, file_points))
#labels_ds = ogr.Open('{}\\{}'.format(path, file_labels))
#lyr = ds.GetLayer()

points = lyr2dict(points_ds.GetLayer(), ['segment_id', 'longitude', 'latitude', 'h_li', 'beam', 'file_name'])

print(points.keys())
#points = filter_by_attr(points, 'type', val='СКАЛЫ-ОСТАНЦЫ')
#labels = lyr2dict(labels_ds.GetLayer(), ['new_id', 'X_WGS84', 'Y_WGS84', 'height'])

t = dtime.datetime.now()
#result = get_nearest(points, labels, x_col='X_WGS84', y_col='Y_WGS84', id_col='new_id', h_col='height')
result = height_from_points(points)
#print(result)
print(dtime.datetime.now()-t)

#result2 = filter_by_distance(result, id_col='new_id', h_col='height', del_empty_vals=True)
#result2['Height'] = result2.pop('height')


fields2export = {
    'segment_id': ogr.OFTInteger,
    #'X_WGS84': ogr.OFTReal,
    #'Y_WGS84': ogr.OFTReal,
    'height': ogr.OFTReal,
    'file_name': ogr.OFTString,
}
dict2shp(r'icesat_points_aoi_height.shp', result, fields2export, epsg=4326, x_coord='longitude', y_coord='latitude')

print(dtime.datetime.now()-t)