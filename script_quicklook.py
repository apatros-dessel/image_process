# -*- coding: utf-8 -*-

from geodata import *
dir_in = r'd:\export\kanopus_ms\krym'
# dir_out = r'd:\kanopus_new\quicklook\Tatarstan'

path_in_list = folder_paths(dir_in, files=True, extension='tif')
# dir_out_3857 = fullpath(dir_out, '3857')
# dir_out_img = fullpath(dir_out, 'img')
# suredir(dir_out_3857)
# suredir(dir_out_img)
# scroll(path_in_list)

for i, path_in in enumerate(path_in_list):
    # if not path_in.endswith('newRGB.tif'):
    # continue
    if path_in.endswith('MS.L2.tif'):
        folder, filename = os.path.split(path_in)
        path_rgb = path_in.replace('L2.tif', 'L2.RGB.tif')
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
                             overwrite=True,
                             alpha=True)
        if res != 0:
            print('Error making RGB: %s' % filename)
            continue
        else:
            dir_out_3857 = dir_out_img = folder
            print('RGB written: %s' % filename)

        try:
            path_out = path_in.replace('L2.tif', 'L2.QL.tif')
            res = MakeQuicklook(path_rgb, path_out, 3857, pixelsize=30, overwrite=False)
            if res == 0:
                QuicklookImage(path_out, path_in.replace('L2.tif', 'L2.IMG.tif'))
                print('{} File saved: {}'.format(i + 1, filename))
            else:
                print('{} File not saved: {}'.format(i + 1, filename))
        except:
            print('{} Error saving file: {}'.format(i + 1, filename))