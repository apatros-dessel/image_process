import os
import gdal
import numpy as np

def tile_limits(x, y, tilesize = 1000):
    x0 = x * tilesize
    y0 = y * tilesize
    x1 = x0 + tilesize
    y1 = y0 + tilesize
    return x0, y0, x1, y1

def slice(ds, band, limits = [0,0,1000,1000]):
    return ds.GetRasterBand(band).ReadAsArray()[limits[0]:limits[2],limits[1]:limits[3]]

def finddata(ds, tilesize=1000):
    x = ds.RasterXSize // tilesize + 1
    y = ds.RasterYSize // tilesize + 1
    tilereport = np.zeros((y, x))
    for i in range(x * y):
        yid = i // x
        xid = i % x
        #tile = slice(ds, 4, tile_limits(yid, xid))
        test = 255 in slice(ds, 4, tile_limits(yid, xid))
        # tilereport[yid, xid] = np.ceil(np.mean(tile))
        #print(yid, xid, np.unique(tile))
        if test:
            tilereport[yid, xid] = 1
    return tilereport


def export_tile(path, ds, tile_limits):
    if os.path.exists(path):
        try:
            check = input('File already exists, replace it y/n?')
            if check.strip().lower() == 'y':
                os.remove(path)
            else:
                raise Exception
        except:
            print('Unable to create tile file: {}'.format(path))
            return

    tile_limits = list(tile_limits)
    assert tile_limits[2] > tile_limits[0]
    assert tile_limits[3] > tile_limits[1]
    x = ds.RasterXSize
    y = ds.RasterYSize
    if tile_limits[0] >= x or tile_limits[1] >= y:
        print('Inappropriate tile_limits for raster size ({},{}) - {}'.format(x, y, tile_limits))
        return
    tile_limits[2] = min([tile_limits[2], x])
    tile_limits[3] = min([tile_limits[3], y])
    newx = tile_limits[2] - tile_limits[0]
    newy = tile_limits[3] - tile_limits[1]

    driver = gdal.GetDriverByName('GTiff')
    newds = driver.Create(path, newx, newy, ds.RasterCount, ds.GetRasterBand(1).DataType)

    for band in range(1, ds.RasterCount + 1):
        newds.GetRasterBand(band).WriteArray(slice(ds, band, tile_limits))

    newds.SetProjection(ds.GetProjection())

    geotrans0 = ds.GetGeoTransform()
    geotrans = list(geotrans0)
    geotrans[0] = geotrans0[0] + geotrans[1] * tile_limits[1]
    geotrans[3] = geotrans0[3] + geotrans[5] * tile_limits[0]
    newds.SetGeoTransform(tuple(geotrans))

    newds = None

    return

# Function for tiling
'''
for i in range(len(datas)):
    y = i // datas.shape[1]
    x = i % datas.shape[1]
    if datas[y,x] == 1:
        name = 'tile_{}_{}.tif'.format(y,x)
        try:
            export_tile(name, ds, tile_limits(y,x))
            print('file_saved: {}'.format(name))
        except:
            print('Cannot save file: {}'.format(name))
'''