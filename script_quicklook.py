# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'd:\terratech\export\Tatarstan_pms'

make_rgb = False

path_in_list = folder_paths(dir_in, files=True, extension='tif')

# scroll(path_in_list)

for i, path_in in enumerate(path_in_list):
    # if not path_in.endswith('newRGB.tif'):
        # continue
    if 'PMS.L2.RGB.tif' in path_in:
        folder, filename = os.path.split(path_in)
        filename_rgb =  filename.replace('L2.RGB.tif', 'L2.RGB.tif')
        path_rgb = os.path.join(folder, filename_rgb)
        # print(folder)
        # print(filename)
        # break
        if make_rgb:
            try:
                res = RasterToImage3(path_in,
                                             path_rgb,
                                             method=2,
                                             band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                                             gamma=0.85,
                                             exclude_nodata=True,
                                             enforce_nodata=0,
                                             band_order=[1, 2, 3],
                                             GaussianBlur=False,
                                             reprojectEPSG=3857,
                                             reproject_method=gdal.GRA_Lanczos,
                                             compress='DEFLATE',
                                             overwrite=False,
                                             alpha=True)
            except:
                res = 1
            if res!=0:
                print('Error making RGB: %s' % filename)
            else:
                print('RGB written: %s' % filename)
        try:
            filename_ql = filename.replace('L2.RGB.tif', 'L2.QL.tif')
            path_ql = os.path.join(folder, filename_ql)
            res = MakeQuicklook(path_rgb, path_ql, 3857, pixelsize=30, overwrite=False)
            if res == 0:
                filename_img = filename.replace('L2.RGB.tif', 'L2.IMG.tif')
                path_img = os.path.join(folder, filename_img)
                QuicklookImage(path_ql, path_img)
                print('{} File saved: {}'.format(i + 1, filename))
            else:
                print('{} File not saved: {}'.format(i + 1, filename))
        except:
            print('{} File not saved: {}'.format(i+1, filename))