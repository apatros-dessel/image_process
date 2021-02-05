from geodata import *

raster_in = r'\\172.21.195.2\thematic\!razmetka\Kanopus\Kanopus_clouds\MS\img\img_mist\KVI_11690_08053_01_KANOPUS_20190823_063854_064034.SCN5.MS.L2.tif'
mask_in = r'\\172.21.195.2\thematic\!razmetka\Kanopus\Kanopus_clouds\MS\shp_hand\shp_hand_mist\maska_for_cut\SCN5_maska_for_cut.shp'
raster_out = r'e:\test\croptest.tif'

MaskRaster(raster_in, mask_in, raster_out)