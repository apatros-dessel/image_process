from geodata import *
from datetime import datetime
path_in = r'e:\kanopus_new\pansharpened\Krym_add/!KV3_08248_06472_00_KANOPUS_20190729_084114_084143.SCN8.PMS.L2.tif'
path_out = r'C:/Users/admin/Desktop/030_REPR_REPR_ZERO_ZERO.tif'

t = datetime.now()
RasterToImage3(path_in,
                           path_out,
                           method=2,
                           band_limits=[(0.01, 0.9998), (0.01, 0.9998), (0.01, 0.9998)],
                           gamma=0.85,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=[1, 2, 3],
                           GaussianBlur=False,
                           reprojectEPSG=3857,
                           reproject_method=gdal.GRA_Lanczos,
                           masked = False,
                           compress='DEFLATE',
                           overwrite=True,
                           alpha=True)
print(datetime.now()-t)