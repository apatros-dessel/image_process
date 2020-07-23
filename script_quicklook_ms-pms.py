# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'e:\rks\resurs_granules_new\RP1_28583_05_GEOTON_20180804_081628_081701.SCN3.PMS.L2.GRN36036032'

path_in_list = folder_paths(dir_in, files=True, extension='tif')
i = 0
for path_in in path_in_list:
    if path_in.endswith('.MS.L2.tif') or path_in.endswith('.PMS.L2.tif') or re.search('.GRN\d+.tif$', path_in):
        i += 1
        folder, filename = os.path.split(path_in)
        filename_rgb =  filename.replace('L2', 'L2.RGB')
        path_rgb = os.path.join(folder, filename_rgb)
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
            continue
        else:
            dir_out_3857 = dir_out_img = folder
            print('RGB written: %s' % filename)
        try:
            filename_ql = filename.replace('L2', 'L2.QL')
            path_ql = os.path.join(folder, filename_ql)
            res = MakeQuicklook(path_rgb, path_ql, 3857, pixelsize=30, overwrite=False)
            if res == 0:
                filename_img = filename.replace('L2', 'L2.IMG')
                path_img = os.path.join(folder, filename_img)
                QuicklookImage(path_ql, path_img)
                print('{} File saved: {}'.format(i, filename))
            else:
                print('{} File not saved: {}'.format(i, filename))
        except:
            print('{} File not saved: {}'.format(i, filename))