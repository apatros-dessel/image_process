import numpy as np
import math
import ogr
import osr
#from copy import deepcopy

# Returns maximum length of the list elements
def list_max_len(list_obj):
    l = 0
    for val in list_obj:
        if len(str(val)) > l:
            l = len(str(val))
    return l

def get_nearest(points, names, x_col='x', y_col='y', id_col='id', h_col='h'):
    l = len(points[id_col])
    points[h_col] = np.full((l), -99999, dtype=float)
    points['names_id'] = np.full((l), -9999, dtype=int)
    points['dist'] = np.zeros((l), dtype=float)
    for i in range(l):
        '''
        dx = abs(names[x_col] - points[x_col][i])
        dx_j = dx.argsort()
        jx = dx_j[0]
        dy = abs(names[y_col] - points[y_col][i])
        dy_j = dy.argsort()
        jy = dy_j[0]
        distances = {x_col: dx, y_col: dy}
        ranges = {x_col: dx_j, y_col: dy_j}
        dist_x = math.sqrt(dx[jx]**2 + dy[jx]**2)
        dist_y = math.sqrt(dx[jy]**2 + dy[jy]**2)
        if dist_x > dist_y:
            min_dist = max_dist = dist_y
            pos = jy
        else:
            min_dist = max_dist = dist_x
            pos = jx
        for id in [x_col, y_col]:
            count = 1
            print(id, ranges[id][:3], distances[id][ranges[id][:3]])
            while distances[id][ranges[id][count]] <= max_dist:
                new_dist = math.sqrt(dx[ranges[id][count]]**2 + dy[ranges[id][count]]**2)
                if new_dist < min_dist:
                    min_dist = new_dist
                    pos = ranges[id][count]
                count += 1
        '''
        #pos, min_dist = nearest_point((points[y_col][i], points[x_col][i]), (names[y_col], names[x_col]), True)
        pos, min_dist = nearest_point_simple((points[y_col][i], points[x_col][i]), (names[y_col], names[x_col]), True)
        points[h_col][i] = names[h_col][pos]
        points['names_id'][i] = names[id_col][pos]
        points['dist'][i] = min_dist
    return points

def nearest_point(point, cloud, return_dist=False):
    dx = abs(cloud[1] - point[1])
    dx_j = dx.argsort()
    jx = dx_j[0]
    dy = abs(cloud[0] - point[0])
    dy_j = dy.argsort()
    jy = dy_j[0]
    distances = [dx, dy]
    ranges = [dx_j, dy_j]
    dist_x = math.sqrt(dx[jx] ** 2 + dy[jx] ** 2)
    dist_y = math.sqrt(dx[jy] ** 2 + dy[jy] ** 2)
    if dist_x > dist_y:
        min_dist = max_dist = dist_y
        pos = jy
    else:
        min_dist = max_dist = dist_x
        pos = jx
    for id in [0,1]:
        count = 1
        #print(id, ranges[id][:3], distances[id][ranges[id][:3]])
        while distances[id][ranges[id][count]] <= max_dist:
            new_dist = math.sqrt(dx[ranges[id][count]] ** 2 + dy[ranges[id][count]] ** 2)
            if new_dist < min_dist:
                min_dist = new_dist
                pos = ranges[id][count]
            count += 1
    if return_dist:
        return (pos, min_dist)
    else:
        return pos

def nearest_point_simple(point, cloud, return_dist=False):
    dx = abs(cloud[1] - point[1])
    dy = abs(cloud[0] - point[0])
    dx = dx*dx
    dy = dy*dy
    dist = np.sqrt(dx+dy)
    pos = dist.argsort()[0]
    if return_dist:
        return (pos, dist[pos])
    else:
        return pos

def lyr2dict(lyr, attr_list, coord_from_geom=False):
    export = {}
    for attr in attr_list:
        export[attr] = []
    for feat in lyr:
        for attr in attr_list:
            export[attr].append(feat.GetField(attr))
    for attr in attr_list:
        export[attr] = np.array(export[attr])
    return export

def filter_by_attr(arr, id_col, val=0, include=False):
    if not id_col in arr:
        raise Exception('No parameter %f found' % id_col)
    if include:
        mask = (arr[id_col]==val)
    else:
        mask = (arr[id_col]!=val)
    arr_new = {}
    for key in arr:
        arr_new[key] = np.copy(arr[key][mask])
    return arr_new

def filter_by_distance(result, id_col = 'id', lab_col='names_id', dist_col='dist', h_col='h', nodata=0, del_empty_vals=False):
    vals, counts = np.unique(result[lab_col], return_counts=True)
    for i in range(len(counts)):
        if counts[i] > 1:
            distances = result[dist_col][result[lab_col]==vals[i]]
            ids = result[id_col][result[lab_col]==vals[i]]
            ids = np.delete(ids, distances.argsort()[0])
            for id in ids:
                result[h_col][result[id_col]==id] = nodata
    if del_empty_vals:
        result = filter_by_attr(result, h_col, val=nodata)
    return result

# Adds the fields to dataset from a list or 1-dim array
def dict2shp(filename, data, attr_list, dtype=ogr.OFTInteger, width=None, epsg=4326, x_coord=None, y_coord=None):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(filename)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    lyr = data_source.CreateLayer('Layer', srs, ogr.wkbPoint)
    l = len(data[data.keys()[0]])
    for key in attr_list:
        if not key in attr_list:
            raise Exception('No parameter %s found' % (key))
        if isinstance(attr_list, dict):
            dtype_ = attr_list[key]
        else:
            dtype_ = dtype
        attr = data[key]
        field = ogr.FieldDefn(key, dtype_)
        if dtype_ == ogr.OFTString:
            if width is None:
                width = list_max_len(attr)
            field.SetWidth(width)
        lyr.CreateField(field)
    for i in range(l):
        feat = ogr.Feature(lyr.GetLayerDefn())
        for key in attr_list:
            feat.SetField(key, data[key][i])
        if x_coord is not None and y_coord is not None:
            if (x_coord in data) and (y_coord in data):
                x = data[x_coord][i]
                y = data[y_coord][i]
                wkt = "POINT(%f %f)" % (float(x), float(y))
                point = ogr.CreateGeometryFromWkt(wkt)
                feat.SetGeometry(point)
        lyr.CreateFeature(feat)
        feat = None
    data_source = None
    return None



