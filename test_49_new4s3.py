from geodata import *

path_raster = r'\\172.21.195.2\FTP-Share\ftp\Aligned_pms\tatarstan_pms'
path_meta = r'\\172.21.195.2\FTP-Share\ftp\s3'
path_s3 = r'e:\rks\s3\kanopus_pms'
prenom = ''

raster_paths = folder_paths(path_raster,1,'tif')
raster_ids = flist(raster_paths, lambda x: prenom + split3(x)[1].replace('.REF',''))
meta_paths = folder_paths(path_meta,1,'json')
meta_ids = flist(meta_paths, lambda x: split3(x)[1])

scroll(raster_ids[:])
# scroll(meta_ids[:10])

def copy_data(raster_path, meta_path, path_s3, id, prenom = ''):
    if not id.startswith(prenom):
        id += prenom
    folder_out = fullpath(path_s3, id)
    suredir(folder_out)
    raster_out = fullpath(folder_out, id, 'tif')
    if not os.path.exists(raster_out):
        shutil.copyfile(raster_path, raster_out)
    meta_out = fullpath(folder_out, id, 'json')
    if not os.path.exists(meta_out):
        shutil.copyfile(meta_path, meta_out)
    temp_ql = tempname('tif')
    ql_out = fullpath(folder_out, id + '.QL', 'tif')
    if not os.path.exists(ql_out):
        MakeQuicklook(raster_out, temp_ql, 3857, pixelsize=30, overwrite=False)
        RasterToImage3(temp_ql,
                       ql_out,
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
    return raster_out, meta_out, ql_out

def correct_meta(raster_path, vector_path, type, ms_part=None, pms_part=None):
    ds_in, lyr_in = get_lyr_by_path(vector_path, 1)
    raster = gdal.Open(raster_path)
    if not (None in (raster, ds_in, lyr_in)):
        for feat in lyr_in:
            # feat = lyr_in.GetFeature(i)
            if (type=='PMS') and not (None in (ms_part, pms_part)):
                id = feat.GetField('id')
                id_new = id.replace(ms_part, pms_part)
                feat.SetField('id', id_new)
            id_neuro = feat.GetField('id_neuro')
            if (type=='PMS') and id_neuro.endswith('L2'):
                id_neuro_new = id_neuro + 'PMS'
                feat.SetField('id_neuro', id_neuro_new)
            feat.SetField('type', type)
            feat.SetField('rows', raster.RasterYSize)
            feat.SetField('cols', raster.RasterXSize)
            trans = raster.GetGeoTransform()
            feat.SetField('x_size', float(trans[1]))
            feat.SetField('y_size', -float(trans[-1]))
            lyr_in.SetFeature(feat)
        ds_in = None
        # print('META_CHANGED: %s' % id_new)
    else:
        print('ERROR CHANGING META: %s' % vector_path)

def CopyCorrect(id, raster_path, type_tmpt_list, prenom = ''):
    meta_ids = globals()['meta_ids']
    meta_paths = globals()['meta_paths']
    success = False
    if id in meta_ids:
        type = None
        for rename in type_tmpt_list:
            ms_part, pms_part = rename
            if ms_part in id:
                type = 'MS'
            elif pms_part in id:
                type = 'PMS'
        if type:
            meta_path = meta_paths[meta_ids.index(id)]
            raster_out, meta_out, ql_out = copy_data(raster_path, meta_path, path_s3, id, prenom=prenom)
            correct_meta(raster_path, meta_out, type, ms_part=ms_part, pms_part=pms_part)
            success = True
        else:
            print('UNRECKOGNIZED TYPE FOR: %s' % id)
            return 1
    else:
        for rename in type_tmpt_list:
            ms_part, pms_part = rename
            if pms_part in id:
                id_new = id.replace(pms_part, ms_part)
                if id_new in meta_ids:
                    meta_path = meta_paths[meta_ids.index(id_new)]
                    raster_out, meta_out, ql_out = copy_data(raster_path, meta_path, path_s3, id, prenom=prenom)
                    correct_meta(raster_path, meta_out, 'PMS', ms_part=ms_part, pms_part=pms_part)
                    success = True
                    break
    if success:
        json_fix_datetime(meta_out)
        print('FILE WRITTEN: %s' % id)
        return 1
    else:
        print('META ID NOT FOUND: %s' % id)
        return 1

for id, raster_path in zip(raster_ids, raster_paths):
    CopyCorrect(id, raster_path, [('_S_', '_PSS4_'),('.MS.','.PMS.')])
    continue
    if id in meta_ids:
        meta_path = meta_paths[meta_ids.index(id)]
        raster_out, meta_out, ql_out = copy_data(raster_path, meta_path, path_s3, id)
        correct_meta(raster_path, vector_path, 'PMS')
        print('FILE WRITTEN: %s' % id)
    elif ('_PSS4_' in id) and (id.replace('_PSS4_', '_S_') in meta_ids):
        id_new = id.replace('_PSS4_', '_S_')
        meta_path = meta_paths[meta_ids.index(id_new)]
        raster_out, meta_out, ql_out = copy_data(raster_path, meta_path, path_s3, id)
        # change_meta(raster_out, meta_out, '_PSS4_', '_S_')
        correct_meta(raster_path, vector_path, 'PMS', ms_part='_S_', pms_part='_PSS4_')
        print('FILE WRITTEN: %s' % id)
    elif ('.PMS.' in id) and (id.replace('.PMS.', '.MS.') in meta_ids):
        id_new = id.replace('.PMS.', '.MS.')
        meta_path = meta_paths[meta_ids.index(id_new)]
        raster_out, meta_out, ql_out = copy_data(raster_path, meta_path, path_s3, id)
        # change_meta(raster_out, meta_out, '.PMS.', '.MS.')
        correct_meta(raster_path, vector_path, 'PMS', ms_part='.MS.', pms_part='.PMS.')
        print('FILE WRITTEN: %s' % id)
    else:
        print('META ID NOT FOUND: %s' % id)