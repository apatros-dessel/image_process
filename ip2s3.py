'''
FUNCTIONS FOR EXPORT SPACE IMAGES TO S3 FORMAT
'''
from geodata import *
from image_processor import process, scene

imsys_list = ['KAN']
references_path = r'\\172.21.195.215\thematic\products\ref\_reference'
rgb_band_order=[1,2,3]
save_rgb=False
ms2pms=False

def FindScenes(path_in, imsys_list = None, skip_duplicates = False, v_cover = None):
    scenes = OrderedDict()
    for folder_in in obj2list(path_in):
        proc = process().input(folder_in, imsys_list=imsys_list, skip_duplicates = skip_duplicates)
        for ascene in proc.scenes:
            id = ascene.meta.id
            if '.PAN' in id:
                base_id = id.replace('.PAN','.PMS')
                type = 'PAN'
            elif '.MS' in id:
                base_id = id.replace('.MS','.PMS')
                type = 'MS'
            elif '.PMS' in id:
                base_id = id
                type = 'PMS'
            else:
                print('Unknown type: %s' % id)
                continue
            if base_id in scenes:
                if type in scenes[base_id]:
                    print('Scene already exists: %s' % id)
                    continue
                else:
                    scenes[base_id][type] = ascene.fullpath
            else:
                scenes[base_id] = {'id': base_id, type: ascene.fullpath}
    # !!! Correct for multiple source folders!
    if not v_cover:
        v_cover = fullpath(folder_in, 'v_cover.json')
    if not os.path.exists(v_cover):
        # scroll(v_cover)
        proc.GetCoverJSON(v_cover)
    return scenes, v_cover

def GetS3Scenes(folder_in):
    scenes = OrderedDict()
    for s3id in os.listdir(folder_in):
        folder = fullpath(folder_in, s3id)
        if os.path.isdir(folder):
            meta_path = fullpath(folder, s3id, 'json')
            if os.path.exists(meta_path):
                meta_ds, meta_lyr = get_lyr_by_path(meta_path)
                if meta_lyr:
                    id = meta_lyr.GetNextFeature().GetField('id')
                    scenes[s3id] = (id, meta_path)
                    continue
            print('Cannot find metadata: %s' % s3id)
    return scenes

def CoverMatch(feat1, feat2, field_list = None):
    if field_list is None:
        field_list = ['id', 'id_s', 'id_neuro', 'datetime', 'sun_elev', 'sun_azim', 'sat_id', 'sat_view', 'sat_azim', 'channels', 'type', 'format', 'rows', 'cols', 'epsg_dat', 'u_size', 'x_size', 'y_size', 'level']
    else:
        field_list = obj2list(field_list)
    geom1 = feat1.GetGeometryRef()
    geom2 = feat2.GetGeometryRef()
    if geom1.Intersects(geom2):
        for field_id in field_list:
            if feat1.GetField(field_id)!=feat2.GetField(field_id):
                return False
    return True

def GetSceneFullpath(scene_dict, type_list = ['PMS', 'MS', 'PAN']):
    type_list = obj2list(type_list)
    for type in type_list:
        scene_fullpath = scene_dict.get(type)
        if scene_fullpath:
            return scene_fullpath
    print('Scene fullpath not found: %s with %s' % (scene_dict.get('id'), ' '.join(list(scene_dict.keys())).strip().replace('id', '').replace('  ',' ')))
    return None

def GetUnmatchingScenes(source_scenes, s3_scenes):
    unmatched = OrderedDict()
    matched = OrderedDict()
    for id in source_scenes:
        for s3id in s3_scenes:
            source_id, meta_path = s3_scenes[s3id]
            if id==source_id:
                scene_dict = source_scenes[id]
                scene_fullpath = GetSceneFullpath(scene_dict)
                if scene_fullpath:
                    source_process = process().input(scene_fullpath)
                    temp_json = tempname('json')
                    source_process.GetCoverJSON(temp_json)
                    source_ds, source_lyr = get_lyr_by_path(temp_json)
                    s3_ds, s3_lyr = get_lyr_by_path(meta_path)
                    if source_lyr and s3_lyr:
                        source_feat = source_lyr.GetNextFeature()
                        s3_feat = s3_lyr.GetNextFeature()
                        match = CoverMatch(source_feat, s3_feat)
                        if match:
                            print('SCENE ALREADY EXIST: %s' % s3id)
                            matched[id] = source_scenes[id]
                            continue
                    else:
                        print('COVER ERROR: %s' % s3id)
                else:
                    print('CANNOT OPEN SCENE: %s' % id)
        unmatched[id] = source_scenes[id]
    return matched, unmatched

def GetQuicklookCheck(source_scenes, xls_quicklook_dict, type=['MS', 'PAN', 'PMS']):
    unmatched = OrderedDict()
    matched = OrderedDict()
    type_list = obj2list(type)
    if xls_quicklook_dict is None:
        print('QUICKLOOK DICT is None, cannot check by quicklook')
        return source_scenes, None
    else:
        keys = list(xls_quicklook_dict.keys())
    for id in source_scenes:
        scene_fullpath = GetSceneFullpath(source_scenes[id], type_list = type_list)
        scroll(scene_fullpath)
        if scene_fullpath is not None:
            if scene_fullpath in keys:
                if xls_quicklook_dict[scene_fullpath]['mark'] == '1':
                    matched[id] = source_scenes[id]
                    print('QUICKLOOK MATCH: %s' % id)
                    continue
        unmatched[id] = source_scenes[id]
        print('QUICKLOOK MISMATCH: %s' % id)
    # scroll(keys)
    return matched, unmatched

def GetReference(file, ref_list):
    match_list = []
    for ref in ref_list:
        match = RasterMatch(file, ref)
        if match==3:
            return ref
        elif match==2:
            match_list.append(ref)
    if len(match_list)>0:
        return match_list[0]
    else:
        print('REFERENCE NOT FOUND FOR: %s' % file)
        return None

def AlignSystem(pin, ref, pout, tempdir=None, align_file=None, reproject_method=gdal.GRA_NearestNeighbour, errors_folder = None,
                overwrite = True):
    if check_exist(pout, ignore=overwrite):
        return False
    base = pin
    if tempdir is None:
        tempdir = os.environ['TMP']
    for tname in ('1.tif', '2.tif', '3.pickle'):
        tpath = fullpath(tempdir, tname)
        if os.path.exists(tpath):
            os.remove(tpath)
    transform = fullpath(tempdir, '3.pickle')
    srs_in = get_srs(gdal.Open(pin))
    srs_ref = get_srs(gdal.Open(ref))

    match = ds_match(srs_in, srs_ref)
    if not match:
        repr_raster = tempname('tif')
        scroll([pin, repr_raster], header='ReprojectRaster source:')
        ReprojectRaster(pin, repr_raster, int(srs_ref.GetAttrValue('AUTHORITY',1)), method=reproject_method)
        pin = repr_raster
    if align_file is None:
        align_file = pin
    elif align_file!=pin:
        srs_align = get_srs(gdal.Open(align_file))
        align_match = ds_match(srs_align, srs_ref)
        if not align_match:
            repr_raster = tempname('tif')
            ReprojectRaster(align_file, repr_raster, int(srs_ref.GetAttrValue('AUTHORITY', 1)), method=reproject_method)
            align_file = repr_raster

    cmd_autoalign = r'python37 autoalign.py {align_file} {ref} {transform} -l -t {tempdir}'.format(
        align_file = align_file.replace(' ', '***'),
        ref = ref.replace(' ', '***'),
        transform = transform,
        tempdir = tempdir
    )
    print('\n%s\n' % cmd_autoalign)
    os.system(cmd_autoalign)

    if os.path.exists(transform):
        cmd_warp = r'python37 warp.py {pin} {transform} {pout} -t {tempdir}'.format(
            pin = pin.replace(' ', '***'),
            transform = transform,
            pout = pout.replace(' ', '***'),
            tempdir = tempdir
        )
        os.system('\n%s\n' % cmd_warp)
        print('\nWRITTEN : %s' % pout)
        res = True
    else:
        print('\nTRANSFORM NOT CREATED FOR: %s' % base)
        if errors_folder:
            suredir(errors_folder)
            f, n, e = split3(pout)
            error_path = fullpath(errors_folder,n,e)
            if not os.path.exists(error_path):
                shutil.copyfile(pin, error_path)
        res = False
    if not match:
        if os.path.exists(repr_raster):
            os.remove(repr_raster)
        else:
            print('File not found: %s' % repr_raster)
    return res

def ReprojectRasterByAlign(pin, ref, pout, tempdir=None, align_file=None, reproject_method=gdal.GRA_NearestNeighbour):
    base = pin
    if tempdir is None:
        tempdir = os.environ['TMP']
    for tname in ('1.tif', '2.tif', '3.pickle'):
        tpath = fullpath(tempdir, tname)
        if os.path.exists(tpath):
            os.remove(tpath)
    transform = fullpath(tempdir, '3.pickle')
    srs_in = get_srs(gdal.Open(pin))
    srs_ref = get_srs(gdal.Open(ref))
    match = ds_match(srs_in, srs_ref)
    if not match:
        repr_raster = tempname('tif')
        ReprojectRaster(pin, repr_raster, int(srs_ref.GetAttrValue('AUTHORITY',1)), method=reproject_method)
        pin = repr_raster
    if align_file is None:
        align_file = pin
    elif align_file!=pin:
        srs_align = get_srs(gdal.Open(align_file))
        align_match = ds_match(srs_align, srs_ref)
        if not align_match:
            repr_raster = tempname('tif')
            ReprojectRaster(align_file, repr_raster, int(srs_ref.GetAttrValue('AUTHORITY', 1)), method=reproject_method)
            align_file = repr_raster
    cmd_autoalign = r'python37 C:\Users\TT\PycharmProjects\pereprivyazka\autoalign.py {align_file} {ref} {transform} -l -t {tempdir}'.format(
        align_file = align_file.replace(' ', '***'),
        ref = ref.replace(' ', '***'),
        transform = transform,
        tempdir = tempdir
    )
    print('\n%s\n' % cmd_autoalign)
    os.system(cmd_autoalign)

    if os.path.exists(transform):
        cmd_warp = r'python37 C:\Users\TT\PycharmProjects\pereprivyazka\warp.py {pin} {transform} {pout} -t {tempdir}'.format(
            pin = pin.replace(' ', '***'),
            transform = transform,
            pout = pout.replace(' ', '***'),
            tempdir = tempdir
        )
        os.system('\n%s\n' % cmd_warp)
        print('\nWRITTEN : %s' % pout)
    else:
        globals()['errors_list'].append(base)
        print('\nTRANSFORM NOT CREATED FOR: %s' % base)
    if not match:
        if os.path.exists(repr_raster):
            os.remove(repr_raster)

def GetReferenceFromList(file, references_list):
    intersect_list = []
    for ref in references_list:
        match = RasterMatch(file, ref)
        if match==3:
            return ref
        elif match==2:
            intersect_list.append(ref)
    if intersect_list:
        return intersect_list[0]
    else:
        return None

def ReprojectSystem(scene_dict, reference_list, folder_out, pms=True, overwrite = False):
    pms_folder = fullpath(folder_out, '__pms')
    pan_folder = fullpath(folder_out, '__pan')
    ms_folder = fullpath(folder_out, '__ms')
    errors_folder = fullpath(folder_out, '__errors')
    id = scene_dict.get('id')
    if id is None:
        print('ERROR: SCENE ID NOT FOUND: {}' % scene_dict)
        return False
    if pms:
        pmspath = fullpath(pms_folder, id, 'tif')
        if os.path.exists(pmspath):
            print('ERROR: PMSPATH EXISTS: %s' % id)
            return False
    else:
        if 'MS' in scene_dict:
            ms = folder_paths(split3(scene_dict['MS'])[0], 1, 'tif')[0]
            mspath = fullpath(ms_folder, id.replace('.PMS', '.MS'), 'tif')
        else:
            print('ERROR: MS FILE NOT FOUND: %s' % id)
            return False
        if os.path.exists(mspath):
            print('ERROR: MSPATH EXISTS: %s' % id)
            return False
    if pms and ('PMS' in scene_dict):
        pms = folder_paths(split3(scene_dict['PMS'])[0],1,'tif')[0]
        ref = GetReference(pms, reference_list)
        if ref:
            suredir(pms_folder)
            AlignSystem(pms, ref, pmspath, align_file=pms, reproject_method=gdal.GRA_Bilinear, errors_folder=errors_folder, overwrite=overwrite)
            return pmspath
        else:
            suredir(errors_folder)
            errpath = fullpath(errors_folder, id, 'tif')
            if os.path.exists(errpath):
                print('ERROR PATH EXISTS: %s' % id)
                return False
            else:
                shutil.copyfile(pms, errpath)
        psp = False
    else:
        psp = True
    if (psp or not pms) and (('MS' in scene_dict) and ('PAN' in scene_dict)):
        ms = folder_paths(split3(scene_dict['MS'])[0],1,'tif')[0]
        pan = folder_paths(split3(scene_dict['PAN'])[0],1,'tif')[0]
        panpath = fullpath(pan_folder, id.replace('.PMS','.PAN'), 'tif')
        mspath = fullpath(ms_folder, id.replace('.PMS', '.MS'), 'tif')
        ref = GetReference(pan, reference_list)
        if ref:
            suredir(ms_folder)
            res_ms = AlignSystem(ms, ref, mspath, align_file=pan, reproject_method=gdal.GRA_Bilinear, errors_folder=errors_folder, overwrite=overwrite)
            if pms and res_ms:
                suredir(pan_folder)
                res_pan = AlignSystem(pan, ref, panpath, align_file=pan, reproject_method=gdal.GRA_Bilinear, errors_folder=errors_folder, overwrite=overwrite)
                if res_pan:
                    cmd_pansharp = r'python py2pci_pansharp.py {} {} {} -d TRUE'.format(panpath, mspath, pmspath)
                    # print(cmd_pansharp)
                    os.system(cmd_pansharp)
                    if os.path.exists(pmspath):
                        print('PANSHARPENING SUCCESSFUL: %s' % id)
                    else:
                        print('PANSHARPENING ERROR: %s' % id)
                        return False
                else:
                    print('CANNOT MAKE PANSHARPENING: PAN ALIGN ERROR: %s' % id)
                    return False
            elif res_ms:
                return mspath
            elif not res_ms:
                print('CANNOT MAKE PANSHARPENING: MS ALIGN ERROR: %s' % id)
                return False
        else:
            suredir(errors_folder)
            mserrpath = fullpath(errors_folder, id.replace('.PMS', '.MS'), 'tif')
            if os.path.exists(mserrpath):
                print('ERROR MSERRPATH EXISTS: %s' % id)
                return False
            else:
                shutil.copyfile(ms, mserrpath)
            if pms:
                panerrpath = fullpath(errors_folder, id.replace('.PMS', '.PAN'), 'tif')
                if os.path.exists(panerrpath):
                    print('ERROR PANERRPATH EXISTS: %s' % id)
                    return False
                else:
                    shutil.copyfile(pan, mserrpath)
                    pmserrpath = fullpath(errors_folder, id, 'tif')
                    if os.path.exists(pmserrpath):
                        print('ERROR PMSERRPATH EXISTS: %s' % id)
                        return False
                    else:
                        cmd_pansharp = r'python py2pci_pansharp.py {} {} {} -d TRUE'.format(mserrpath, mserrpath, pmserrpath)
                        print(cmd_pansharp)
                        if os.path.exists(pmserrpath):
                            print('ERROR PANSHARPENING SUCCESSFUL: %s' % id)
                        else:
                            print('ERROR PANSHARPENING ERROR: %s' % id)
                            return False
    else:
        return False
    return True

def CheckIdFromList(info, test_ids, pms=True):
    matched = []
    missed = []
    for test_id in test_ids:
        miss = True
        if pms:
            if re.search('.MS', test_id):
                continue
            elif re.search('_S_', test_id):
                continue
        else:
            if re.search('.PMS', test_id):
                continue
            elif re.search('_PSS4_', test_id):
                continue
        test_id_corr = test_id.replace('*', '.*').replace('3NP2_\d+', '.*')
        fr_search = re.search('^fr\d+_', test_id_corr)
        if fr_search:
            test_id_corr = test_id_corr[len(fr_search.group()):]
        if re.search('\dscn', test_id_corr):
            test_id_corr = test_id_corr.replace('scn', '.SCN')
        for s3id in info:
            id = info[s3id].get('id')
            if id:
                if re.search(test_id_corr, id):
                    matched.append(s3id)
                    miss = False
                    break
            else:
                print('ID not found: %s' % s3id)
                pass
        if miss:
            print(test_id, test_id_corr)
            missed.append(test_id)
    return matched, missed

def Names4S3(path_in, folder_out, id, type=None, ext='tif'):
    if type:
        id_type = '%s.%s' % (id, type)
    else:
        id_type = id
        if ext.lower() in ('json', 'geojson'):
            type = 'JSON'
    path_out = fullpath(folder_out, id_type, ext)
    if not os.path.exists(path_in):
        print('ERROR: %s source not found: %s' % (type, path_in))
        return False
    elif os.path.exists(path_out):
        print('WARNING: %s file exists: %s' % (type, path_out))
        return 0
    else:
        return path_out

def RGB4S3(path_in, folder_out, id, band_order=[1,2,3]):
    rgb_out = Names4S3(path_in, folder_out, id, 'RGB')
    if rgb_out:
        try:
            RasterToImage3(path_in,
                           rgb_out,
                           method=2,
                           band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                           gamma=0.80,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=band_order,
                           GaussianBlur=False,
                           # reprojectEPSG=3857,
                           reproject_method=gdal.GRA_Bilinear,
                           compress='DEFLATE',
                           overwrite=False,
                           alpha=True)
            return True
        except:
            print('Error making RGB: %s' % id)
            return False
    elif rgb_out==0:
        return True

def Quick4S3fromRGB(rgb_in, folder_out, id):
    ql_out = Names4S3(rgb_in, folder_out, id, 'QL')
    if ql_out:
        try:
            MakeQuicklook(rgb_in, ql_out, 3857, pixelsize=30, overwrite=False)
            return True
        except:
            print('Error making quicklook: %s' % id)
            return False
    elif ql_out==0:
        return True

def Quick4S3(path_in, folder_out, id, band_order=[1,2,3]):
    ql_out = Names4S3(path_in, folder_out, id, 'QL')
    if ql_out:
        temp_ql = tempname('tif')
        try:
            MakeQuicklook(path_in, temp_ql, 3857, pixelsize=30, overwrite=False, method=gdal.GRA_NearestNeighbour)
            RasterToImage3(temp_ql,
                           ql_out,
                           method=2,
                           band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                           gamma=0.80,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=band_order,
                           GaussianBlur=False,
                           # reprojectEPSG=3857,
                           reproject_method=gdal.GRA_Bilinear,
                           compress='DEFLATE',
                           overwrite=False,
                           alpha=True)
            res = True
        except:
            print('Error making QL: %s.QL.tif' % id)
            res = False
        finally:
            if os.path.exists(temp_ql):
                os.remove(temp_ql)
            return res
    elif ql_out==0:
        return True

# !!! The case of Resursp granules processing is not integrated
def JSON4S3(path_in, folder_out, id, ms2pms=False, raster_path=None):
    json_out = Names4S3(path_in, folder_out, id, None, 'json')
    if json_out:
        if ms2pms:
            get_pms_json(path_in, json_out, id, pms_raster_path=raster_path)
        else:
            filter_dataset_by_col(path_in, 'id', id, path_out=json_out, raster_match=raster_path)
        if os.path.exists(json_out):
            ds_out, lyr_out = get_lyr_by_path(json_out)
            if lyr_out is None:
                print('JSON metadata file not created: %s' % id)
                ds_out = None
                os.remove(json_out)
                return False
            elif len(lyr_out) == 0:
                print('JSON metadata file is empty: %s' % id)
                ds_out = None
                os.remove(json_out)
                return False
            return True
        else:
            print('Error making JSON metadata: %s' % id)
            return False
    elif json_out==0:
        return True

def get_pms_json(path_cover, path_out, pms_id, pms_raster_path=''):
    if os.path.exists(path_out):
        print('FILE EXISTS: %s' % path_out)
        return 1
    if not os.path.exists(path_cover):
        print('Cannot find path: {}'.format(path_cover))
        return 1
    ms_id = pms_id.replace('.PMS', '.MS')
    filter_dataset_by_col(path_cover, 'id', ms_id, path_out=path_out, raster_match=pms_raster_path)
    pms_ds, pms_lyr = get_lyr_by_path(path_out, 1)
    if pms_lyr is None:
        print('FILE NOT FOUND: %s' % path_out)
        return 1
    elif len(pms_lyr)==0:
        print('EMPTY LAYER: %s' % path_out)
        pms_ds = None
        os.remove(path_out)
        return 1
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
        trans = pms_data.GetGeoTransform()
        if trans:
            feat.SetField('x_size', float(trans[0]))
            feat.SetField('y_size', -float(trans[-1]))
        else:
            feat.SetField('x_size', None)
            feat.SetField('y_size', None)
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
    # print('PMS data successfully written for for %s' % pms_id)
    return 0

def Scene4S3(raster_data_in, vector_cover_in, folder_out, id, rgb_band_order=[1,2,3], save_rgb=False, ms2pms=False):
    if not os.path.exists(raster_data_in):
        print('Raster data not found: %s' % raster_data_in)
        return False
    if not os.path.exists(vector_cover_in):
        print('Vector cover not found: %s' % vector_cover_in)
        return False
    scene_folder = fullpath(folder_out, id)
    suredir(scene_folder)
    scene_data = fullpath(scene_folder, id, 'tif')
    if os.path.exists(scene_data):
        print('WARNING: DATA file exists: %s' % scene_data)
    else:
        shutil.copyfile(raster_data_in, scene_data)
    result = OrderedDict()
    result['DATA'] = True
    if save_rgb:
        result['RGB'] = RGB4S3(scene_data, scene_folder, id, band_order=rgb_band_order)
        result['QL'] = Quick4S3fromRGB(scene_data.replace('.tif', '.RGB.tif'), scene_folder, id)
    else:
        result['QL'] = Quick4S3(scene_data, scene_folder, id, band_order=[1,2,3])
    result['JSON'] = JSON4S3(vector_cover_in, scene_folder, id, ms2pms=ms2pms, raster_path=scene_data)
    scroll(result, header='Report %s:' % id)

# Scene4S3(raster_data_in, vector_cover_in, folder_out, id, rgb_band_order=[1,2,3], save_rgb=save_rgb, ms2pms=ms2pms)