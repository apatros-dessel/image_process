from acherep import *

bandpath_green = (r'e:\test\newsnt\S2A_MSIL2A_20190828_RGBN.tif', 2)
bandpath_red = (r'e:\test\newsnt\S2A_MSIL2A_20190828_RGBN.tif', 1)
bandpath_nir = (r'e:\test\newsnt\S2A_MSIL2A_20190828_RGBN.tif', 4)
bandpath_swir1 = (r'e:\test\newsnt\S2A_MSIL2A_20190828_SWIR-2.tif', 2)
bandpath_swir2 = (r'e:\test\newsnt\S2A_MSIL2A_20190828_SWIR-2.tif', 3)

out_raster_forest = r'e:\test\newsnt\S2A_MSIL2A_20190828_MFT.tif'
out_raster_fire = r'e:\test\newsnt\S2A_MSIL2A_20190828_MFR.tif'
out_vector = r'e:\test\newsnt\S2A_MSIL2A_20190828_MFT.shp'

out_raster_UFC = r'e:\test\newsnt\S2A_MSIL2A_20190828_UFC.tif'
out_raster_FAR = r'e:\test\newsnt\S2A_MSIL2A_20190828_FAR.tif'

'''
ForestMask(bandpath_red,
           bandpath_nir,
           image_metadata = {'date': '19000101', 'sensor': 'S2A'},
           red=[100, 500],
           nir=[1000, 3100],
           threshold = 60,
           min_pixel_num = 6,
           output_shapefile=None,
           output_cirfile=out_raster_forest,
           compress = 'LZW')
'''

BurnedMask(bandpath_green,
           bandpath_red,
           bandpath_nir,
           bandpath_swir1,
           bandpath_swir2,
           image_metadata = {'date': '19000101', 'sensor': 'S2A'},
           index_value = 6,
           min_pix_num=6,
           output_raster=out_raster_fire,
           output_shapefile=None,
           output_UFC=out_raster_UFC,
           output_FAR=out_raster_FAR,
           compress='LZW')
