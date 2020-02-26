from image_processor import *

path_in = r'd:\digital_earth\planet_rgb\new\20190910\20190910_062218_1049_3B_AnalyticMS.tif'
path_out = r'e:\test\test_repr.tif'

t = datetime.now()
geodata.ReprojectRaster(path_in, path_out, 3857, compress = 'LZW')
# geodata.Mosaic(path_in, path_out)

print(datetime.now()-t)