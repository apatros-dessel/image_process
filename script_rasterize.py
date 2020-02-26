from geodata import RasterizeVector

path_in_raster = r'E:\rks\digital_earth\neuro\20190912_082257_1038_3B_AnalyticMS.tif'

path_in_vector = r'E:\rks\digital_earth\neuro\69_QUARRY_PLN_20190912.shp'

path_out = r'E:\rks\digital_earth\neuro\rasterized_vector.tif'

RasterizeVector(path_in_vector, path_in_raster, path_out)