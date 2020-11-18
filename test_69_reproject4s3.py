# Reproject Kanopus source data and prepear for uploading to S3 server

from geodata import *
from image_processor import process

folder_in = r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\102_2020_1339'
# txt_names_in = None #r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\102_2020_1339\2020-07-08_1418.txt'
folder_out = r'd:\digital_earth\KV_Tatarstan'
references_path = r'\\172.21.195.2\FTP-Share\ftp\References'
source_name_tmpt = r'fr13_kv1_33892_26862_01.' # fr1_KV3_13044_10269_01_3NP2_20_S_584506_090620.tif
align_renaming_template = (r'fr.+_s_.+$', '_S_', '_PSS1_')
folder_pansharp = None

'''
STAGES
1. Find all scenes available in source data sorting them by location and image type (PAN, MS, PMS)
2. Check if some of the scenes are already processed
3. Reproject source images from PMS data
4. If PMS data is not available, reproject PAN and MS and make pansharpening
5. Prepare PMS data for S3
6. If reprojection was failed, save the source data separately
'''

def FindScenes(path_in):
    scenes = OrderedDict()
    for folder_in in obj2list(path_in):
        proc = process.input(folder_in)
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
                scenes[base_id] = {type: ascene.fullpath}
    return scenes

def GetS3Scenes(folder_in):
    scenes = OrderedDict()
    for s3id in os.listdir(folders):
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

def GetUnmatchingScenes(source_scenes, s3_scenes):
    unmatched = OrderedDict()
    for id in source_scenes:
        for s3id in s3_scenes:
            source_id, meta_path = s3_scenes[s3id]
            if id==source_id:
                source_scene = scene(source_scenes[id])
                temp_json = tempname(json)
                source_scene.GetCoverJSON(temp_json)
                source_ds, source_lyr = get_lyr_by_path(temp_json)
                s3_ds, s3_lyr = get_lyr_by_path(meta_path)
                if source_lyr and s3_lyr:
                    source_feat = source_lyr.GetNextFeature(source_lyr)
                    s3_feat = source_lyr.GetNextFeature(s3_lyr)
                    match = CoverMatch(source_feat, s3_feat)
                    if match:
                        print('SCENE ALREADY EXIST: %s' % s3id)
                        continue
                else:
                    print('COVER ERROR: %s' % s3id)
        unmatched[id] = source_scenes[id]
    return unmatched

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

def GetReferenceFromList(file, reference_list):
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

def ReprojectSystem(scene_dict, reference_list, folder_out):
    pms_folder = fullpath(folder_out, '_pms')
    if 'PMS' in scene_dict:
        pms = align_file = scene_dict['PMS']
    elif ('MS' in scene_dict) and ('PAN' in scene_dict):
        ms = scene_dict['MS']
        pan = align_file = scene_dict['PAN']
    else:
        scroll(scene_dict, header='FILES NOT FOUND:')



reproject_methods_dict = {
    'NN': gdal.GRA_NearestNeighbour,
    'AVG': gdal.GRA_Average,
    'BIL': gdal.GRA_Bilinear,
    'CUB': gdal.GRA_Cubic,
    'CSP': gdal.GRA_CubicSpline,
    'LCS': gdal.GRA_Lanczos,
}

folder_errors = r'{}\errors'.format(folder_out)

errors_list = []

composition = OrderedDict()

references_in = folder_paths(references_path,1,'tif')


def raster_geom(ds, reference=None):
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
    wkt = template % r1
    if sys.version.startswith('2'):
        geom = ogr.Geometry(wkt=wkt)
    else:
        geom = ogr.CreateGeometryFromWkt(wkt, reference)
    return geom

def raster_match(path1, path2):
    geosrs1 = raster_params(path1)
    geosrs2 = raster_params(path2)
    if None in (geosrs1, geosrs2):
        return None, None
    else:
        srs1, geom1 = geosrs1
        srs2, geom2 = geosrs2
    crs_match = srs1.GetAttrValue('AUTHORITY',1) == srs2.GetAttrValue('AUTHORITY',1)
    # print(srs1.GetAttrValue('AUTHORITY',1), srs2.GetAttrValue('AUTHORITY',1), crs_match)
    if not crs_match:
        geom1.TransformTo(srs2)
    result = 2 * int(geom1.Intersects(geom2)) + crs_match
    return result


proc = process().input(folder_in, skip_duplicates=False)
temp_cover = fullpath(folder_in, 'vector_cover.json')
if not os.path.exists(temp_cover):
    proc.GetCoverJSON(temp_cover)
files = []
for ascene in proc.scenes:
    scene_folder = ascene.path
    raster_files = folder_paths(scene_folder,1,'tif')
    if len(raster_files)==1:
        files.append(raster_files[0])
    else:
        scroll(raster_files, header=r'Passed %s' % ascene.meta.id)

scroll(files)
sys.exit()
# if not txt_names_in in (None, ''):
    # files = open(txt_names_in).read().split('\n')
# else:
    # files = folder_paths(folder_in, 1, 'tif')
# names = flist(files, lambda x: split3(x)[1])

# scroll(files, lower='len=%s Finish it?' % len(files))

# fin = input()
# print(bool(int(fin)))
# if bool(int(fin)):
    # sys.exit()

suredir(folder_out)
print(files)

print('\nSTART REFERENCING %i FILES' % len(files))
count = 0
for file in files:
    count+=1
    print(count, "/", len(files))
    fail = True
    p,n,e = split3(file)

    if re.search(source_name_tmpt, n.lower()) is None:
        print("wrong name pattern", n.lower())
        continue
    composition[file] = OrderedDict()
    align_file = file
    if re.search(align_renaming_template[0], n.lower()):
        fr1, fr2 = align_renaming_template[1:]
        align_name = n.replace(fr1, fr2)
        '''
        if align_name in names:
            align_id = names.index(align_name)
            align_file = files[align_id]
        else:
            align_file = file
        '''
        for i, name in enumerate(names):
            align_file_new = files[i]
            if raster_match(align_file_new, file)==3:
                align_file = align_file_new
                print('Align file found: %s' % align_file)
                break
            else:
                print('False align file: %s' % align_file)
    composition[file]['align_file'] = align_file
    print(n, folder_out)
    pout = fullpath(folder_out, n + '.REF', e)
    exist = False
    composition[file]['output_file'] = pout
    if os.path.exists(pout):
        print('\nFILE ALREADY EXISTS: %s' % pout)
        # continue
        exist = True

    intersect_dict = OrderedDict()
    for ref in references_in:
        match = raster_match(align_file, ref)
        if match==3:
            if exist == True:
                print("match == 3; trying reproject with bilinear")
                pout3 = fullpath(folder_out, n + '.REF_new', e)
                align_system(file, ref, pout3, align_file=align_file, reproject_method=gdal.GRA_Bilinear)
            else:
                print("match == 3; didn't exist")
                align_system(file, ref, pout, align_file=align_file)
            fail = False
            break
        else:
            intersect_dict[ref] = match
    # print(file)
    if fail:
        scroll(intersect_dict)
        for ref in intersect_dict:
            if intersect_dict[ref] == 2:
                # pout2 = fullpath(folder_out, n + '.REF2', e)
                align_system(file, ref, pout, align_file=None, reproject_method=gdal.GRA_Bilinear)
                # for method_id in reproject_methods_dict:
                    # pout_new = pout.replace('.tif', '_%s.tif' % method_id)
                    # align_system(file, ref, pout_new, align_file=None, reproject_method=reproject_methods_dict[method_id])
                fail = False
                break
    if fail:
        globals()['errors_list'].append(os.path.basename(file))
        print('REFERENCE NOT FOUND FOR: %s' % file)

dict_to_xls(fullpath(folder_out, 'reprojection_report.xls'), composition)

if folder_pansharp:
    cmd_pansharp = 'python pci_psh_kan-rsp.py {pin} {pout}'.format(
        pin = folder_out,
        pout = folder_pansharp,
    )
    print(cmd_pansharp)
    os.system(cmd_pansharp)

if errors_list:
    scroll(errors_list, header='\nERRORS:')
    print('\n')
    print('; '.join(flist(errors_list, os.path.basename)))

