from geodata import *
from datetime import datetime
path_in = r'\\172.21.195.2\FTP-Share\ftp\proc\resurs\Krym\pms\RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.PMS.L2.tif'
path_out = r'\\172.21.195.2\FTP-Share\ftp\proc\resurs\Krym\rgb\RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.PMS.L2.RGB.tif'

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