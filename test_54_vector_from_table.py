import os, ogr, osr
import pandas as pd
import numpy as np

table_in = r'C:\Users\admin\Documents\Книга1.xlsx'
json_out = r'C:\Users\admin\Documents\polygon.json'
x_col = 'x'
y_col = 'y'
type = 'MULTIPOLYGON'
object_col = 'object'
crs = 4326
order_col = None

def WktFromDataFrame(frame, x_col, y_col, type):
    x_coords = list(frame[x_col])
    y_coords = list(frame[y_col])
    if type=='MULTILINESTRING':
        wkt = 'MULTILINESTRING (('
        for x, y in zip(x_coords, y_coords):
            wkt += '%s %s,' % (str(float(x)), str(float(y)))
        wkt = wkt[:-1] + '))'
    elif type=='MULTIPOLYGON':
        wkt = 'MULTIPOLYGON ((('
        for x, y in zip(x_coords, y_coords):
            wkt += '%s %s,' % (str(float(x)), str(float(y)))
        start = (x_coords[0], y_coords[0])
        fin = (x_coords[-1], y_coords[-1])
        if start!=fin:
            wkt = wkt + '%s %s)))' % (str(float(x_coords[0])), str(float(y_coords[0])))
        else:
            wkt = wkt[:-1] + ')))'
    else:
        print('Wrong geometry type: %s' % type)
        return None
    return wkt

def TableToJSON(pout, frame, x_col, y_col, type, order_col, object_col, crs, overwrite=True):
    if os.path.exists(pout):
        if overwrite:
            try:
                os.remove(pout)
            except:
                return 'Cannot remove file: %s' % pout
        else:
            return 'File already exists: %s' % pout
    type = str(type).upper()
    driver = ogr.GetDriverByName('GeoJSON')
    ds_out = driver.CreateDataSource(pout)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(crs)
    lyr_out = ds_out.CreateLayer('', srs = srs)
    defn = lyr_out.GetLayerDefn()

    if type=='POINT':
        x_coords = frame[x_col]
        y_coords = frame[y_col]
        for x, y in zip(x_coords, y_coords):
            feat = ogr.Feature(defn)
            wkt = 'POINT (%s %s)' % (str(float(x)), str(float(y)))
            geom = ogr.CreateGeometryFromWkt(wkt, srs)
            feat.SetGeometry(geom)
            lyr_out.CreateFeature(feat)

    elif type in ('MULTILINESTRING', 'MULTIPOLYGON'):
        object_ids = np.unique(frame[object_col])
        object_gen = frame.groupby(object_col)
        for id in object_ids:
            object_frame = object_gen.filter(lambda x: list(x[object_col])[0]==id)
            feat = ogr.Feature(defn)
            wkt = WktFromDataFrame(object_frame, x_col, y_col, type)
            if wkt:
                geom = ogr.CreateGeometryFromWkt(wkt, srs)
                feat.SetGeometry(geom)
                lyr_out.CreateFeature(feat)

    ds_out = None

if table_in.endswith('.xls') or  table_in.endswith('.xlsx'):
    frame = pd.read_excel(table_in, sheet_name='Лист1')

TableToJSON(json_out, frame, x_col, y_col, type, order_col, object_col, crs, overwrite=True)