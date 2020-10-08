from geodata import *

folder_in = r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\102_2020_1339'
txt_names_in = None #r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus\102_2020_1339\2020-07-08_1418.txt'
folder_out = r'd:\digital_earth\KV_Tatarstan'
references_path = r'\\172.21.195.2\FTP-Share\ftp\References'
source_name_tmpt = r'fr13_kv1_33892_26862_01.' # fr1_KV3_13044_10269_01_3NP2_20_S_584506_090620.tif
align_renaming_template = (r'fr.+_s_.+$', '_S_', '_PSS1_')
folder_pansharp = None

reproject_methods_dict = {
    'NN': gdal.GRA_NearestNeighbour,
    'AVG': gdal.GRA_Average,
    'BIL': gdal.GRA_Bilinear,
    'CUB': gdal.GRA_Cubic,
    'CSP': gdal.GRA_CubicSpline,
    'LCS': gdal.GRA_Lanczos,
}

errors_list = []

composition = OrderedDict()

references_in = folder_paths(references_path,1,'tif')

def raster_params(pin):
    ds = gdal.Open(pin)
    if ds is None:
        print('Raster not found: %s' % pin)
        return None
    srs = get_srs(ds)
    geom = raster_geom(ds, srs)
    return srs, geom

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

def align_system(pin, ref, pout, tempdir=None, align_file=None, reproject_method=gdal.GRA_NearestNeighbour):
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


if not txt_names_in in (None, ''):
    files = open(txt_names_in).read().split('\n')
else:
    files = folder_paths(folder_in, 1, 'tif')
names = flist(files, lambda x: split3(x)[1])

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

