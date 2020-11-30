# Reproject Kanopus source data and prepear for uploading to S3 server

from geodata import *
from image_processor import process, scene

folder_in = r'\\172.21.195.215\thematic\source\ntzomz\102_2020_1276'
folder_out = r'd:\rks\s3\kanopus_missed\1276_MS'
references_path = r'\\172.21.195.215\thematic\products\ref\_reference'
test_ids_txt = r'\\172.21.195.215\thematic\products\s3\kanopus\missed_pms.txt'
folder_s3 = r'\\172.21.195.215\thematic\products\s3\kanopus'
pms = False
overwrite = False

'''
STAGES
1. Find all scenes available in source data sorting them by location and image type (PAN, MS, PMS)
2. Check if some of the scenes are already processed
3. Reproject source images from PMS data
4. If PMS data is not available, reproject PAN and MS and make pansharpening
5. Prepare PMS data for S3
6. If reprojection was failed, save the source data separately
'''

def FindScenes(path_in, skip_duplicates = False):
    scenes = OrderedDict()
    for folder_in in obj2list(path_in):
        proc = process().input(folder_in, skip_duplicates = skip_duplicates)
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
    return scenes

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

def GetSceneFullpath(scene_dict):
    for type in ['PMS', 'MS', 'PAN']:
        scene_fullpath = scene_dict.get(type)
        if scene_fullpath:
            return scene_fullpath

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
        ms = folder_paths(split3(scene_dict['MS'])[0], 1, 'tif')[0]
        mspath = fullpath(ms_folder, id.replace('.PMS', '.MS'), 'tif')
        if os.path.exists(mspath):
            print('ERROR: MSPATH EXISTS: %s' % id)
            return False
    if pms and ('PMS' in scene_dict):
        pms = folder_paths(split3(scene_dict['PMS'])[0],1,'tif')[0]
        ref = GetReference(pms, reference_list)
        if ref:
            suredir(pms_folder)
            AlignSystem(pms, ref, pmspath, align_file=pms, reproject_method=gdal.GRA_Bilinear, errors_folder=errors_folder, overwrite=overwrite)
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
                    print(cmd_pansharp)
                    os.system(cmd_pansharp)
                    print(cmd_pansharp)
                    if os.path.exists(pmspath):
                        print('PANSHARPENING SUCCESSFUL: %s' % id)
                    else:
                        print('PANSHARPENING ERROR: %s' % id)
                        return False
                else:
                    print('CANNOT MAKE PANSHARPENING: PAN ALIGN ERROR: %s' % id)
                    return False
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


reference_list = folder_paths(references_path,1,'tif')
test_ids = open(test_ids_txt).read().split('\n')

source_scenes = FindScenes(folder_in)
s3_scenes = GetS3Scenes(folder_s3)
matched, unmatched = GetUnmatchingScenes(source_scenes, s3_scenes)

# match, miss = CheckIdFromList(unmatched, test_ids, pms=True)
''' REPORT OF MATCHING AND UNMATCHING FILES
scroll(unmatched, lower=len(unmatched))
name = os.path.split(folder_in)[1]
matched_list = list(matched.keys())
scroll(matched_list, lower=len(matched_list))
with open(fullpath(folder_out, name+'_matched', 'txt'), 'w') as txt:
    txt.write('\n'.join(matched_list))
unmatched_list = list(unmatched.keys())
scroll(unmatched_list, lower=len(unmatched_list))
with open(fullpath(folder_out, name+'_missed', 'txt'), 'w') as txt:
    txt.write('\n'.join(unmatched_list))
'''

success = []
fail = []
for id in unmatched:
    # if id in match:
        # print(id)
        # continue
        res = ReprojectSystem(unmatched[id], reference_list, folder_out, pms=pms, overwrite=overwrite)
        if res:
            success.append(id)
        else:
            # fail.append(id)
            pass
sys.exit()

scroll(success, header='SUCCESS', lower=len(success))
scroll(fail, header='FAIL', lower=len(fail))