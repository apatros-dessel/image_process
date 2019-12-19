# -*- coding: utf-8 -*-

from image_processor import *

path = r'c:\sadkov\minprod\planet\composites\2019-09-10\image'
basepath = r'c:\sadkov\minprod\planet\cashe\gari_20190910.tif'
path2export = r'c:\sadkov\minprod\planet\images\gari_fall_new.tif'
shp_name = r'minprod_planet_cover.shp'

import_list = []
file_list = os.listdir(path)
scroll(file_list)
for file in file_list:
    if file.endswith('.tif'):
        import_list.append(fullpath(path, file))
import_list.reverse()
scroll(import_list)

base_raster = geodata.gdal.Open(basepath)
prj = base_raster.GetProjection()
geotrans = base_raster.GetGeoTransform()
xsize = base_raster.RasterXSize
ysize = base_raster.RasterYSize
band_num = 3
dt = 1

geodata.mosaic(import_list,
               path2export,
               prj,
               geotrans,
               xsize,
               ysize,
               band_num,
               dt,
               nptype=np.int8,
               method=geodata.gdal.GRA_CubicSpline,
               exclude_nodata=True,
               enforce_nodata=None,
               compress = 'LERC_DEFLATE')