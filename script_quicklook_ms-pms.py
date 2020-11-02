# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'e:\rks\resurs_granules_newnew'

path_in_list = folder_paths(dir_in, files=True, extension='tif')
i = 0
for path_in in path_in_list:
    if path_in.endswith('.MS.L2.tif') or path_in.endswith('.PMS.L2.tif') or re.search('.GRN\d+.tif$', path_in):
        i += 1
        f,n,e = split3(path_in)
        filename_rgb =  n + '.RGB.' + e
        path_rgb = os.path.join(f, filename_rgb)

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
            print('%i Error making RGB: %s' % (i, n))
            # continue
        else:
            print('%i RGB written: %s' % (i, n))
        try:
            filename_ql = n + '.QL.' + e
            path_ql = os.path.join(f, filename_ql)
            res = MakeQuicklook(path_rgb, path_ql, 3857, pixelsize=30, overwrite=False)
            if res == 0:
                filename_img = n + '.IMG.' + e
                path_img = os.path.join(f, filename_img)
                QuicklookImage(path_ql, path_img)
                print('{} File saved: {}'.format(i, n))
            else:
                print('{} File not saved: {}'.format(i, n))
        except:
            print('{} Error saving file: {}'.format(i, n))