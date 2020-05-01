from image_processor import *

path_in = r'd:\kanopus_new\quicklook\Krym\3857'
path_out = r'd:\kanopus_new\quicklook\Krym_mosaic.tif'

path_in_list = folder_paths(path_in)[1]

t = datetime.now()
# geodata.ReprojectRaster(path_in, path_out, 3857, compress = 'LZW')
geodata.Mosaic(path_in_list, path_out, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9'])

print(datetime.now()-t)