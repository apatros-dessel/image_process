# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'd:\terratech\export\krym_resurs_pms'
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
    if 'PMS.L2__' in path_in:
        folder, filename = os.path.split(path_in)
        filename_rgb =  filename.replace('L2__', 'L2.RGB__')
        path_rgb = os.path.join(folder, filename_rgb)
        # print(folder)
        # print(filename)
        # break
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
        if res!=0:
            print('Error making RGB: %s' % filename)
            continue
        else:
            dir_out_3857 = dir_out_img = folder
            print('RGB written: %s' % filename)
        try:
            path_out = path_rgb.replace('L2.RGB', 'L2.QL')
            res = MakeQuicklook(path_rgb, path_out, 3857, pixelsize=30, overwrite=False)
            if res == 0:
                QuicklookImage(path_out, path_in.replace('L2.RGB', 'L2.IMG'))
                print('{} File saved: {}'.format(i+1, filename))
            else:
                print('{} File not saved: {}'.format(i + 1, filename))
        except:
            print('{} File not saved: {}'.format(i+1, filename))