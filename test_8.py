# -*- coding: utf-8 -*-

# Calculates differenses between two radar elevation values to get forest height

from min_dist import *
import datetime as dtime
'''
path = 'c:\\sadkov\\forest\\dem'
file_points = r'relief_points_severnoye.shp'
file_labels = r'relief_labels_severnoye.shp'
'''

def height_from_points(points, beam_attr='beam', segment_attr='segment_id', file_attr='file_name', x_attr='longitude', y_attr='latitude', elev_attr='h_li', extra_dem=None, take_canopy_coords=False):
    heights = {
        segment_attr: [],
        file_attr: [],
        x_attr: [],
        y_attr: [],
        'height': [],
        'corr': []
    }
    beams = [['gt1r', 'gt1l'], ['gt2r', 'gt2l'], ['gt3r', 'gt3l']]
    for beam in beams:
        ground_set = filter_by_attr(points, beam_attr, val=beam[0], include=True)
        #print(len(points[elev_attr]), len(ground_set[elev_attr]))
        canopy_set = filter_by_attr(points, 'beam', val=beam[1], include=True)
        for id in range(len(ground_set[elev_attr])):
            if ground_set[elev_attr][id] is not None and ground_set[elev_attr][id]!=0:
                for id2 in range(len(canopy_set[elev_attr])):
                    if canopy_set[elev_attr][id2] is not None and canopy_set[elev_attr][id2]!=0:
                        if ground_set[segment_attr][id] == canopy_set[segment_attr][id2]:
                            if ground_set[file_attr][id] == canopy_set[file_attr][id2]:
                                heights[segment_attr].append(ground_set[segment_attr][id])
                                heights[file_attr].append(ground_set[file_attr][id])
                                height_val = float(canopy_set[extra_dem][id2]) - float(ground_set[elev_attr][id])
                                if extra_dem is not None:
                                    h_g = float(ground_set[extra_dem][id])
                                    h_c = float(canopy_set[extra_dem][id2])
                                    if (h_g != 0) and (h_c != 0):
                                        #dh = h_c - h_g
                                        dh = h_g - h_c # logically incorrect version I try in despair
                                        height_val = height_val - dh # height val = h_c(icesat) - h_g(icesat) - (h_c(dem) - h_g(dem))
                                        heights['corr'].append(1)
                                else:
                                    heights['corr'].append(0)
                                heights['height'].append(height_val)
                                if take_canopy_coords:
                                    heights[x_attr].append(canopy_set[x_attr][id2])
                                    heights[y_attr].append(canopy_set[y_attr][id2])
                                else:
                                    heights[x_attr].append(ground_set[x_attr][id])
                                    heights[y_attr].append(ground_set[y_attr][id])
    return heights

path = r'C:\sadkov\forest\dem\saga\new'
file_points = r'icesat_points_aoi_dem.shp'

t = dtime.datetime.now()
points_ds = ogr.Open('{}\\{}'.format(path, file_points))


points = lyr2dict(points_ds.GetLayer(), ['segment_id', 'longitude', 'latitude', 'h_li', 'beam', 'file_name', 'dem_srtm', 'dem_alos-p', 'dem_aster', 'dem_topo'])

t = dtime.datetime.now()

fields2export = {
    'segment_id': ogr.OFTInteger,
    'longitude': ogr.OFTReal,
    'latitude': ogr.OFTReal,
    'height': ogr.OFTReal,
    'file_name': ogr.OFTString,
    'corr': ogr.OFTInteger,
}
for dem_name in ['dem_topo']:
    result = height_from_points(points, extra_dem=dem_name, take_canopy_coords=True)
    dict2shp(r'C:\sadkov\forest\icesat\new\icesat_points_aoi_height_corr3_%s.shp' % dem_name, result, fields2export, epsg=4326, x_coord='longitude', y_coord='latitude')
    print(dtime.datetime.now() - t)

print(dtime.datetime.now()-t)