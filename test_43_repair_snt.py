from geodata import *

pin = r'e:\rks\razmetka\set032__20200807__forests_sentinel_sverdlovsk\images\sentinel'

files = folder_paths(pin,1,'tif')

for p in files:
    f,n,e = split3(p)
    if '!' in n:
        continue
    # if not n.lower().startswith('s2a'): continue
    # new = n.replace('IM11','IM10')
    new = '!' + n
    if new == n:
        new = '!' + n
    raster = gdal.Open(p, 1)
    count = raster.RasterCount
    new_raster = ds(fullpath(f,new,e),copypath=p,options={'bandnum':count,'dt':3,'compress':'DEFLATE','nodata':0}, editable=True)

    for i in range(1, count+1):
        arr_ = raster.GetRasterBand(i).ReadAsArray()
        # if i==10:
            # continue
        # elif i==11:
            # i = 10
        o = np.unique(arr_)[0]
        arr_[arr_ == o] = 0
        new_raster.GetRasterBand(i).WriteArray(arr_)
        # raster.GetRasterBand(i).SetNoDataValue(0)

    raster = None
    new_raster = None

    print('Raster written: %s with %i bands' % (n,count))
