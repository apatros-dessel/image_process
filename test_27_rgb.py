from geodata import *
from datetime import datetime

files = folder_paths(r'd:\rks\Irkutsk\rgb\Landsat',1,'tif')
suredir(r'd:\rks\Irkutsk\rgb_8bit_fix2\Landsat')
for path_in in files:
    path_out = r'd:\rks\Irkutsk\rgb_8bit_fix2\Landsat\%s_8bit_1proc.tif' % Name(path_in)
    t = datetime.now()
    RasterToImage3(path_in,
                               path_out,
                               method=2,
                               # band_limits = [(0.02, 0.98), (0.02, 0.98), (0.02, 0.98)],
                               band_limits=[(0.006, 0.9998), (0.006, 0.9998), (0.006, 0.9998)],
                               # band_limits=[(2, 4), (2, 4), (2, 4)],
                               data_limits=[(6000, 15000), (6000, 15000), (6000, 15000)], # Landsat RGB
                               # data_limits=[(500, 5500), (200, 4200), (200, 4200)], # Sentinel SWIR
                               # data_limits=[(6000, 21000), (6000, 21000), (6000, 21000)], # Landsat SWIR
                               # data_limits=[(200, 1800), (200, 1800), (200, 1800)], # Sentinel RGB
                               gamma=0.85,
                               exclude_nodata=True,
                               enforce_nodata=0,
                               band_order=[1, 2, 3],
                               GaussianBlur=False,
                               reprojectEPSG=None,
                               reproject_method=gdal.GRA_Lanczos,
                               masked = False,
                               compress='DEFLATE',
                               overwrite=False,
                               alpha=True)
    print(datetime.now()-t)