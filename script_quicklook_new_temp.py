# -*- coding: utf-8 -*-

from geodata import *

dir_in = r'd:\digital_earth\KV_Nizhniy'
txt_ids = None#r'd:\digital_earth\KV_Tatarstan\kv_ids.txt'\\172.21.195.2\FTP-Share\ftp\s3\sentinel_krasnoyarsk\
dir_out = r'd:\digital_earth\KV_Nizhniy'
preserve_original = False
make_rgb = False

names_tmpt = {
    'sentinel': '^S2[AB]_MSI.+\d$',
    'planet': '.*AnalyticMS(_SR)?$',
    'planet_neuro': 'IM4-PLN.*',
    'kanopus': 'KV.+L2$',
    #'resursp': 'RP.+L2$',
    'resursp-grn': 'RP.+PMS\.L2\.GRN\d+$',
    'kanopus_new_ref': '^fr.+KV.+$'
}

bands_dict = {
    'sentinel': [3,2,1],
    'planet': [3,2,1],
    'planet_neuro': [1,2,3],
    'kanopus': [1,2,3],
    #'resursp': 'RP.+L2$',
    'resursp-grn': [1,2,3],
    'kanopus_new_ref': [1,2,3]
}


def valid_str(str_, tmpt_list):
    # tmpt_list = obj2list(tmpt_list)
    if isinstance(tmpt_list, dict):
        tmpt_list = tmpt_list.values()
    for tmpt in tmpt_list:
        if re.search(tmpt, str_):
            return True
    return False

def get_band_order(n):
    names_tmpt = globals()['names_tmpt']
    for key in names_tmpt:
        tmpt = names_tmpt[key]
        if re.search(tmpt, n):
            return globals()['bands_dict'][key]

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

def get_pms_json(path_cover, path_out, pms_id, pms_raster_path=''):

    if os.path.exists(path_out):
        filter_dataset_by_col(path_dict['json'], 'id', pms_id, path_out=path_out)
        old_ds, old_lyr = get_lyr_by_path(path_out)
        if len(old_lyr) > 0:
            return 0

    # print('Original PMS data not found for %s, collecting data from MS' % pms_id)

    if not os.path.exists(path_cover):
        print('Cannot find path: {}'.format(path_cover))
        return 1

    ms_id = pms_id.replace('.PMS', '.MS')
    filter_dataset_by_col(path_cover, 'id', ms_id, path_out=path_out)

    pms_ds, pms_lyr = get_lyr_by_path(path_out, 1)

    feat = pms_lyr.GetNextFeature()
    feat.SetField('id', pms_id)
    feat.SetField('id_neuro', feat.GetField('id_neuro') + 'PMS')
    feat.SetField('type', 'PMS')

    if os.path.exists(pms_raster_path):
        pms_data = gdal.Open(pms_raster_path)
    else:
        pms_data = None
    if pms_data is not None:
        feat.SetField('rows', int(pms_data.RasterYSize))
        feat.SetField('cols', int(pms_data.RasterXSize))
        feat.SetField('x_size', float(pms_data.GetGeoTransform[0]))
        feat.SetField('y_size', -float(pms_data.GetGeoTransform[5]))
    else:
        pan_id = pms_id.replace('.PMS', '.PAN')
        tpan_path = filter_dataset_by_col(path_cover, 'id', pan_id)
        pan_ds, pan_lyr = get_lyr_by_path(tpan_path)
        pan_feat = pan_lyr.GetNextFeature()
        feat.SetField('rows', int(pan_feat.GetField('rows')))
        feat.SetField('cols', int(pan_feat.GetField('cols')))
        feat.SetField('x_size', float(pan_feat.GetField('x_size')))
        feat.SetField('y_size', float(pan_feat.GetField('y_size')))
    # feat.SetField('area', None)

    pms_lyr.SetFeature(feat)

    pms_ds = None

    print('PMS data successfully written for for %s' % pms_id)

    return 0

def NullCheck(file):
    if os.path.exists(file):
        vals = np.unique(gdal.Open(file).ReadAsArray())
        if len(vals)==1 and vals[0]==0:
            return True
        else:
            return False
    else:
        print('File not found: %s' % file)
        return True

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
        if NullCheck(path_in):
            print('%i -- file skipped: file is empty -- %s' % (i, n))
            continue
        band_order = get_band_order(n)
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
                                             band_order=band_order,
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
                                           band_order=band_order,
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
        elif os.path.exists(fullpath(f,n.replace('.PMS.','.MS.'),'json')):
            json_out = fullpath(id_dir_out, n, 'json')
            get_pms_json(fullpath(f,n.replace('.PMS.','.MS.'),'json'), json_out, n, pms_raster_path=path_in)

if report:
    with open(fullpath(dir_out, 'scene_list.txt'), 'w') as txt:
        txt.write('\n'.join(report))
