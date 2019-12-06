from osgeo import ogr, osr, gdal
import os
import numpy as np
#import csv
import xlwt

r_path = r'C:\sadkov\lsat8\testfast'
s_path = r'C:\sadkov\lsat8\test'
s_name = r'test_val_polygon_utm37.shp'
r_namelist = [r'LS08_173027_20180406_NDVI.TIF',
         r'LS08_173027_20180609_NDVI.TIF',
         r'LS08_173027_20180727_NDVI.TIF',
         r'LS08_173027_20180828_NDVI.TIF',
         r'LS08_173027_20180929_NDVI.TIF']
outpath = r'C:\sadkov\test\testexport.xls'

s_name = (s_path + '\\' + s_name)
r_namelist = r_namelist[0:1]

# Find id column in the attributes
def id_from_shp(lyr, new_id = None):
    id_namelist = ['id', 'ID', 'Id']
    if new_id is not None:
        id_namelist.append(new_id)
    featDef = lyr.GetLayerDefn()
    for id_num in range(featDef.GetFieldCount()):
        fieldDef = featDef.GetFieldDefn(id_num)
        if fieldDef.GetNameRef() in id_namelist:
            id_list = [fieldDef.GetNameRef()]
            lyr.ResetReading()
            feat = lyr.GetNextFeature()
            while feat is not None:
                id_list.append(feat.GetFieldAsInteger(id_num))
                feat = lyr.GetNextFeature()
            return id_list
    id_list = range(len(lyr))
    id_list.insert(0, 'NoId')
    return id_list

def shp_grid_stat(s_data, r_namelist):
    lyr = s_data.GetLayer()
    #feat = lyr.GetNextFeature()
    #geom = feat.GetGeometryRef()
    #s_proj = geom.GetSpatialReference()
    s_proj = lyr.GetSpatialRef()
    id_list = id_from_shp(lyr)
    export = [id_list]
    for r_name in r_namelist:
        #print r_name
        r_data = gdal.Open(r_name)
        trans = r_data.GetGeoTransform()
        #print trans
        xo, yo, pw, ph = trans[0], trans[3], trans[1], trans[5]
        r_proj = osr.SpatialReference()
        r_proj.ImportFromWkt(r_data.GetProjectionRef())
        #print 'shp_proj: ', str(s_proj), '\nraster_proj: ', r_proj
        if s_proj != r_proj:
            s_trans = osr.CoordinateTransformation(s_proj, r_proj)
        r_band = r_data.GetRasterBand(1)
        #col = list()
        r_stats = []
        lyr.ResetReading()
        feat = lyr.GetNextFeature()
        while feat is not None:
            geom = feat.GetGeometryRef()
            #print(str(geom))
            if s_proj != r_proj:
                geom = geom.Transform(s_trans)
            #print(str(geom))
            geom = feat.GetGeometryRef()
            #print(str(geom))
            # Get extent
            if (geom.GetGeometryName() == 'MULTIPOLYGON'):
                count = 0; pointsX = []; pointsY = []
                for polygon in geom:
                    geomInner = geom.GetGeometryRef(count)
                    ring = geomInner.GetGeometryRef(0)
                    numpoints = ring.GetPointCount()
                    for p in range(numpoints):
                        lon, lat, z = ring.GetPoint(p)
                        pointsX.append(lon); pointsY.append(lat)
                    count +=1
            elif (geom.GetGeometryName() == 'POLYGON'):
                #print(geom)
                ring = geom.GetGeometryRef(0)
                #print(ring)
                numpoints = ring.GetPointCount()
                pointsX = []; pointsY = []
                for p in range(numpoints):
                    #print(ring.GetPoint(p))
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon); pointsY.append(lat)
            else:
                sys.exit("ERROR: Wrong geometry type, needs POLYGON or MULTIPOLYGON")
            xmin = min(pointsX); xmax = max(pointsX)
            ymin = min(pointsY); ymax = min(pointsY)
            #XminmaxY = [min(pointsX), max(pointsX), min(pointsY), max(pointsY)]
            xoff, yoff = int((xmin - xo) / pw), int((yo - ymax) / pw)
            xcount, ycount = int((xmax - xmin) / pw) + 1, int((ymax - ymin) / pw) + 1

            # process raster
            #print( xmin, pw, 0, ymax, 0, ph )
            target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
            target_ds.SetGeoTransform(( xmin, pw, 0, ymax, 0, ph ))
            raster_srs = osr.SpatialReference()
            raster_srs.ImportFromWkt(r_data.GetProjectionRef())
            target_ds.SetProjection(raster_srs.ExportToWkt())

            gdal.RasterizeLayer(target_ds, [1], lyr, burn_values = [1])

            banddataraster = r_data.GetRasterBand(1)
            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float32)
            bandmask = target_ds.GetRasterBand(1)
            datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float32)
            zoneraster = np.ma.masked_array(dataraster, np.logical_not(datamask))

            f_stats = [np.sum(bandmask), np.min(zoneraster), np.max(zoneraster),
              np.mean(zoneraster), np.std(zoneraster)]
            r_stats.append(f_stats)
            feat = lyr.GetNextFeature()
        export.append(r_stats)
    return export

def stats_to_xls(outpath, export):
    stats_namelist = ['SUM', 'MIN', 'MAX', 'AVG', 'STD']
    wb = xlwt.Workbook()
    for sheet_num in range(5):
        ws = wb.add_sheet(stats_namelist[sheet_num])
        row = ws.row(0)
        row.write(export[0][0], 0)
        for col_num in range(1, len(r_namelist) + 1):
            row.write(r_namelist[col_num - 1], col_num)
        for row_num in range(1, len(export[0])):
            row = ws.row(row_num)
            row.write(export[0][row_num], 0)
            for col_num in range(len(export)):
                row.write(export[col_num - 1][row_num - 1][sheet_num], col_num)
    wb.save(outpath)
    return None

# os.chdir(s_path)
s_data = ogr.Open(s_name)
#lyr = s_data.GetLayer()
#print(lyr.GetSpatialRef())
os.chdir(r_path)

export = shp_grid_stat(s_data, r_namelist)

stats_to_xls(export, outpath)

'''
print export
with open('rep.csv', 'w') as csv_file:
    write = csv.writer(csv_file, delimiter=';')
    for line in export:
        write.writerow(line)
'''
