# -*- coding: utf-8 -*-

from image_processor import process, scene
from geodata import *

path_in = r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\Ostashkovskoe\Case1\May\cut1\ostashkovskoe_2020may_cut1_PSScene4band_b21bb6c5-2af9-439c-912b-cc9a8492c0b2\files\PSScene4Band'
path_out = r'e:\rks\mosaics\Planet_mosaic_test.tif'

# path_in_list = folder_paths(path_in,1,'tif')
rgblist = []
for ascene in process().input(path_in, imsys_list=['PLN']):
    file = ascene.get_raster_path('Analytic')
    f,n,e = split3(file)
    if re.search(r'^\d{8}_.+_3B_AnalyticMS$',n):
        path_rgb = fullpath(r'e:\rks\mosaics',n+'.RGB',e)
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
Mosaic(path_rgb, path_out, band_num=3, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'BIGTIFF=YES'])

print(datetime.now()-t)