# -*- coding: utf-8 -*-

from image_processor import process, scene
from geodata import *

path_in = r'd:\digital_earth\planet_20200920\clip_fire_madashenskoye_2019aug6_PSScene4Band_a2bedcfb-061c-4030-bc96-673cad6e30d3'
path_out = r'd:\digital_earth\planet_20200920\2019aug6\Planet_mosaic_madashenskoye_2019aug6.tif'

folder_out, name_out, ext_out = split3(path_out)
suredir(folder_out)

# path_in_list = folder_paths(path_in,1,'tif')
rgblist = []

for ascene in process().input(path_in, imsys_list=['PLN']).scenes:
    file = ascene.get_raster_path('Analytic')
    f,n,e = split3(file)
    if re.search(r'^\d{8}_.+_3B_AnalyticMS_clip$',n):
        path_rgb = fullpath(folder_out,n+'.RGB',e)
        up_lim = 1 - (float(get_from_tree(ascene.meta.container.get('xmltree'), 'cloudCoverPercentage')[0])/100.0)
        res = RasterToImage3(file,
                                             path_rgb,
                                             method=2,
                                             band_limits=[(0.01, up_lim), (0.01, up_lim), (0.01, up_lim)],
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
        rgblist.append(path_rgb)
        print('Saved: %s' % n)
    else:
        print('Wrong name format: %s' % n)

t = datetime.now()
# ReprojectRaster(path_in, path_out, 3857, compress = 'LZW')
Mosaic(rgblist, path_out, band_num=3, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'BIGTIFF=YES', 'NUM_THREADS=ALL_CPUS'])

print(datetime.now()-t)