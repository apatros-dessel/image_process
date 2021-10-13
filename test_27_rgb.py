from geodata import *
from datetime import datetime

folder_in = r'\\172.21.195.2\exchanger\Popov\Хайлову_11_10_21'
files = folder_paths(folder_in,1,'tif',filter_folder=['out','OUT'])
end_folder = 'd:\\test\\'
suredir(r'd:\test\SR+PMS')
for path_in in files:
    path_out = end_folder + path_in[len(folder_in):]
    suredir(os.path.split(path_out)[0])
    t = datetime.now()
    RasterToImage3(path_in,
                               path_out,
                               method=2,
                               # band_limits = [(0.02, 0.98), (0.02, 0.98), (0.02, 0.98)],
                               band_limits=[(0.006, 0.9998), (0.006, 0.9998), (0.006, 0.9998)],
                               # band_limits=[(2, 4), (2, 4), (2, 4)],
                               # data_limits=[(6000, 15000), (6000, 15000), (6000, 15000)], # Landsat RGB
                               # data_limits=[(500, 5500), (200, 4200), (200, 4200)], # Sentinel SWIR
                               # data_limits=[(6000, 21000), (6000, 21000), (6000, 21000)], # Landsat SWIR
                               # data_limits=[(200, 1800), (200, 1800), (200, 1800)], # Sentinel RGB
                               # data_limits=[(100, 2700), (100, 2700), (100, 2700)],  # Kanopus Resurs RGB
                               data_limits=[(100, 750), (100, 750), (100, 750)],  # Kanopus Resurs RGB
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