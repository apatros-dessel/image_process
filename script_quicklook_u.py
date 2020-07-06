# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'e:\rks\s3'

names_tmpt = {
    'sentinel': '^S2[AB]_MSI.+\d$',
    'planet': '.*AnalyticMS(_SR)?$',
    'planet_neuro': 'IM4-PLN.*',
}

def valid_str(str_, tmpt_list):
    tmpt_list = obj2list(tmpt_list)
    for tmpt in tmpt_list:

        if re.search(tmpt, str_):
            return True
    return False

path_in_list = folder_paths(dir_in, files=True, extension='tif')

for i, path_in in enumerate(path_in_list):

    f, n, e = split3(path_in)

    if valid_str(n, names_tmpt.values()):
        n_rgb =  n + '.RGB'
        path_rgb = fullpath(f, n_rgb, e)
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
            print('Error making RGB: %s' % n)
        else:
            print('RGB written: %s' % n)
        try:
            n_ql = n + '.QL'
            path_ql = fullpath(f, n_ql, e)
            res = MakeQuicklook(path_rgb, path_ql, 3857, pixelsize=30, overwrite=False)
            if res != 0:
                print('Error making QL: %s' % n_ql)
            else:
                print('QL written: %s' % n_ql)
            try:
                n_img = n + '.IMG'
                path_img = fullpath(f, n_img, e)
                QuicklookImage(path_ql, path_img)
                print('IMG written: %s' % n_img)
            except:
                print('Error making IMG: %s' % n_img)
        except:
            print('{} File not saved: {}'.format(i+1, n))