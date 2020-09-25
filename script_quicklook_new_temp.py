# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'e:\rks\ref\nizhniy_pms'
txt_ids = None # r'\\172.21.195.2\FTP-Share\ftp\images\102_2020_1913\MS_1913.txt'
dir_out = r'e:\rks\ref\nizhniy_pms'
preserve_original = False
make_rgb = False

names_tmpt = {
    'sentinel': '^S2[AB]_MSI.+\d$',
    'planet': '.*AnalyticMS(_SR)?$',
    'planet_neuro': 'IM4-PLN.*',
    'kanopus': 'KV.+L2$',
    'resursp': 'RP.+L2$',
    'resursp-grn': 'RP.+GRN\d+$',
    'kanopus_new_ref': '^fr.+KV.+REF$'
}

def valid_str(str_, tmpt_list):
    # tmpt_list = obj2list(tmpt_list)
    if isinstance(tmpt_list, dict):
        tmpt_list = tmpt_list.values()
    for tmpt in tmpt_list:
        if re.search(tmpt, str_):
            return True
    return False

def copymove(file_in, file_out, preserve_original):
    if file_in==file_out:
        print('ERROR: IN AND OUT PATHS ARE THE SAME')
    elif not os.path.exists(file_in):
        print('FILE NOT FOUND: %s' % file_in)
    elif os.path.exists(file_out):
        print('FILE ALREADY EXISTS: %s' % file_out)
    elif preserve_original:
        shutil.copyfile(file_in, file_out)
    else:
        shutil.move(file_in, file_out)

path_in_list = folder_paths(dir_in, files=True, extension='tif')
names_in_list = flist(path_in_list, lambda x: split3(x)[1])

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
        suredir(id_dir_out)
        raster_out = fullpath(id_dir_out, n, e)
        copymove(path_in, raster_out, preserve_original)
        report.append(n)

        # if make_rgb:
        if make_rgb:
            # Add RGB
            id_rgb = n + '.RGB'
            rgb_out = fullpath(id_dir_out, id_rgb, 'tif')
            rgb_in = fullpath(f,id_rgb,'tif')
            if os.path.exists(rgb_in):
                copymove(rgb_in, rgb_out, preserve_original)
            else:
                try:
                    RasterToImage3(raster_out,
                                             rgb_out,
                                             method=2,
                                             band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                                             gamma=0.80,
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
                    print('%i Error making RGB: %s' % (i, n))

            # Add quicklook
            id_ql = n + '.QL'
            ql_out = fullpath(id_dir_out, id_ql, e)
            ql_in = fullpath(f, id_ql, 'tif')
            if os.path.exists(ql_in):
                copymove(ql_in, ql_out, preserve_original)
            else:
                try:
                    MakeQuicklook(rgb_out, ql_out, 3857, pixelsize=30, overwrite=False)
                except:
                    print('{} Error making quicklook: {}'.format(i, n))

        else:
            # Add quicklook
            id_ql = n + '.QL'
            ql_out = fullpath(id_dir_out, id_ql, e)
            ql_in = fullpath(f,id_ql,'tif')
            if os.path.exists(ql_in):
                copymove(ql_in, ql_out, preserve_original)
            else:
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

        # Copy json
        json_in = fullpath(f,n,'json')
        if os.path.exists(json_in):
            json_out = fullpath(id_dir_out, n, 'json')
            if json_in!=json_out:
                shutil.copyfile(json_in, json_out)
                print('%i JSON written %s' % (i, n))

if report:
    with open(fullpath(dir_out, 'scene_list.txt'), 'w') as txt:
        txt.write('\n'.join(report))
