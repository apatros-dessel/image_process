# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'e:\rks\resurs_granules_newnew'
txt_ids = None # r'\\172.21.195.2\FTP-Share\ftp\images\102_2020_1913\MS_1913.txt'
dir_out = r'e:\rks\resurs_granules_newnew'

names_tmpt = {
    'sentinel': '^S2[AB]_MSI.+\d$',
    'planet': '.*AnalyticMS(_SR)?$',
    'planet_neuro': 'IM4-PLN.*',
    'kanopus': 'KV.+L2$',
    'resursp': 'RP.+L2$',
    'resursp-grn': 'RP.+GRN\d+$',
}

def valid_str(str_, tmpt_list):
    tmpt_list = obj2list(tmpt_list)
    for tmpt in tmpt_list:
        if re.search(tmpt, str_):
            return True
    return False

path_in_list = folder_paths(dir_in, files=True, extension='tif')

if txt_ids not in (None, ''):
    ids = open(txt_ids).read().split('\n')
else:
    ids = False

report = []

for i, path_in in enumerate(path_in_list):

    f, n, e = split3(path_in)

    if valid_str(n, names_tmpt.values()):

        if ids:
            if n not in ids:
                print('%i -- file skipped: not in filter -- %s' % (i, n))
                continue

        id_dir_out = fullpath(dir_out, n)
        raster_out = fullpath(id_dir_out, n, e)
        if os.path.exists(raster_out):
            print('%i -- file exists -- %s' % (i, n))
        else:
            shutil.copyfile(path_in, raster_out)
        report.append(n)

        # Add quicklook
        temp_ql = tempname('tif')
        if check_exist(fullpath(id_dir_out, n + '.QL', e), False):
            print('%i -- file exists -- %s.QL.tif' % (i, n))
        else:
            MakeQuicklook(raster_out, temp_ql, 3857, pixelsize=30, overwrite=False)
            RasterToImage3(temp_ql,
                           fullpath(id_dir_out, n + '.QL', e),
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
            os.remove(temp_ql)
        try:
            temp_ql = tempname('tif')
            if check_exist(fullpath(id_dir_out, n + '.QL', e), False):
                print('%i -- file exists -- %s.QL.tif' % (i, n))
            else:
                MakeQuicklook(raster_out, temp_ql, 3857, pixelsize=30, overwrite=False)
                RasterToImage3(temp_ql,
                               fullpath(id_dir_out, n + '.QL', e),
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
                os.remove(temp_ql)
        except:
            print('Error making QL: %s.QL.tif' % n)

        # Add image
        try:
            n_img = n + '.IMG'
            path_img = fullpath(id_dir_out, n_img, e)
            QuicklookImage(path_ql, path_img)
            print('IMG written: %s' % n_img)
        except:
            print('Error making IMG: %s' % n_img)

if report:
    with open(fullpath(dir_out, 'scene_list.txt'), 'w') as txt:
        txt.write('\n'.join(report))
