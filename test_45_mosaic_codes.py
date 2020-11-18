# -*- coding: utf-8 -*-

from image_processor import process, scene
from geodata import *
import matplotlib.pyplot as plt

path_in = r'E:\planet_mosaics\clip_fire_madashenskoye_2019aug2_PSScene4Band_da0b65ba-2700-4d2e-9eee-6980e8089f49'
path_out = r'\\172.21.195.2\FTP-Share\ftp\planet_20200920\2019aug2_hist\Planet_mosaic_madashenskoye_2019aug2.tif'

folder_out, name_out, ext_out = split3(path_out)
suredir(folder_out)

# path_in_list = folder_paths(path_in,1,'tif')
rgblist = []
files_list = []
codes_list = []
def get_code(file_name):
    vals = file_name.split('_')
    if len(vals) == 6:
        return vals[2]
    return vals[3]


codes_dict = {}
for ascene in process().input(path_in, imsys_list=['PLN']).scenes:
    file = ascene.get_raster_path('Analytic')
    f,n,e = split3(file)
    code = get_code(n)
    if re.search(r'^\d{8}_.+_3B_AnalyticMS_clip$',n):
        files_list.append(file)
        codes_list.append(code)
        path_rgb = fullpath(folder_out,n+'.RGB',e)

        if code not in codes_dict.keys():
            codes_dict[code] = [file]
        else:
            codes_dict[code].append(file)
        rgblist.append(path_rgb)
        print('appended: %s' % n)
    else:
        print('Wrong name format: %s' % n)

file_limits = {}
for code in codes_list:
    limits = GetRasterPercentileUInteger(codes_dict[code], 0.02, 0.98, bands=[1, 2, 3], nodata=0, max=65536)
    for f in codes_dict[code]:
        file_limits[f] = limits

for i in range(0, len(files_list)):
    path_rgb = rgblist[i]
    code = codes_list[i]
    file = files_list[i]


    res = RasterToImage3(file,
                                         path_rgb,
                                         method=3,
                                         band_limits=file_limits[file],
                                         gamma=0.85,
                                         exclude_nodata=True,
                                         enforce_nodata=0,
                                         band_order=[3, 2, 1],
                                         GaussianBlur=False,
                                         reprojectEPSG=3857,
                                         reproject_method=gdal.GRA_Lanczos,
                                         compress='DEFLATE',
                                         overwrite=False,
                                         alpha=True)
    print("saved: %s" % path_rgb)

t = datetime.now()
# ReprojectRaster(path_in, path_out, 3857, compress = 'LZW')
Mosaic(rgblist, path_out, band_num=3, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'BIGTIFF=YES', 'NUM_THREADS=ALL_CPUS'])

print(datetime.now()-t)