from geodata import *
from progress.bar import IncrementalBar

meta_folder = r'\\172.21.195.2\thematic\Sadkov_SA\code\razmetka_params'

sattelites = xls_to_dict(fullpath(meta_folder, 'sattelites.xls'))
legend = xls_to_dict(fullpath(meta_folder, 'legend.xls'))
bands = xls_to_dict(fullpath(meta_folder, 'bands.xls'))

report_col_order = ['img_in', 'vec_in', 'img_out', 'msk_out', 'shp_out', 'x_pix_count', 'y_pix_count', 'x_pix_size', 'y_pix_size',
                        'data_min', 'data_max', 'matrix_check', 'bits_exceed', 'msk_values']

def FilesDict(folder, ext, mark = None):
    files = {}
    # scroll(os.listdir(folder), header=folder, counts=1)
    for file in os.listdir(folder):
        fname, fext = os.path.splitext(file)
        if mark is not None:
            if not mark in fname:
                continue
        if fext[1:] == ext:
            files[fname] = fullpath(folder, file)
    return files

def CheckFolder(folder, create = False, message = ''):
    if not os.path.exists(folder):
        if create:
            os.makedirs(folder)
        else:
            raise FileNotFoundError(message + folder)

def GetSattelite(id, col = 'folder', return_sat = False):
    sattelites = globals()['sattelites']
    for sat in sattelites:
        if re.search(sattelites[sat].get('tmpt', '^$'), id):
            if return_sat:
                return sat
            return sattelites[sat].get(col, sat)

def GetBandList(id):
    band_str = globals()['sattelites'].get(GetSattelite(id, return_sat = 1), {}).get('bands')
    if band_str is None:
        raise RazmetkaError('Cannot extract bands for ' + id)
    else:
        count = 0
        band_list = band_str.split(',')
        for i, band in enumerate(band_list):
            band_id_mark = globals()['bands'].get(band, {}).get('short_name')
            if band_id_mark is None:
                raise RazmetkaError('Cannot extract band id mark ' + band + ' for ' + scene.id)
            band_list[i] = ([i+1], band_id_mark)
        return band_list

def KeyMarkedCount(keys, mark):
    i = 0
    for key in keys:
        if mark in key:
            i += 1
    return i

def RasterAlign(pin, ref, pout, tempdir = None, align_file = None, reproject_method = gdal.GRA_NearestNeighbour):
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
    else:
        print('\nTRANSFORM NOT CREATED FOR: %s' % base)
    if not match:
        if os.path.exists(repr_raster):
            os.remove(repr_raster)

def CheckImage(img_in, bands):
    raster = gdal.Open(img_in)
    if len(bands) != raster.RasterCount:
        return True, len(bands)
    for i in bands:
        band = raster.GetRasterBand(i)
        minimum = band.GetMinimum()
        maximum = band.GetMaximum()
        if (minimum is not None) or (maximum is not None):
            if (minimum < 0) or (maximum > 65535):
                raise RazmetkaError( 'Data values out of limits: ' + img_in)
            if (band.DataType!=2) or (band.GetNoDataValue()!=0):
                return True, raster.RasterCount
    return False, raster.RasterCount

# Записать растр снимка в установленном формате
# Если минимальное или максимальное значение данных имеют занимают от 1% всех данных, они принимаются за nodata
def RepairImage(img_in, img_out, bands):
    d = isinstance(bands, dict)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum': len(bands), 'dt':2, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(bands, range(1, len(bands)+1)):
        init_band = raster.GetRasterBand(bin)
        arr_ = init_band.ReadAsArray()
        init_nodata = init_band.GetNoDataValue()
        if init_nodata is None:
            init_nodata=0
            uniques, counts = np.unique(arr_, return_counts=True)
            total_sum = np.sum(counts)
            if counts[0]/total_sum>0.01:
                init_nodata=uniques[0]
            elif counts[-1]/total_sum>0.01:
                init_nodata=uniques[-1]
        arr_[arr_==init_nodata] = 0
        if d:
            multiplicator = bands.get(bin)
            if multiplicator is not None:
                arr_ = arr_ * multiplicator
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    new_raster = None
    return img_out

def SetImage(img_in, img_out, bands, overwrite = False):
    if os.path.exists(img_out):
        repair, counter = CheckImage(img_out, bands)
        if not (repair or overwrite):
            return img_out
    if os.path.exists(img_in):
        repair, counter = CheckImage(img_in, bands)
    else:
        raise FileNotFoundError(img_in)
    if repair:
        return RepairImage(img_in, img_out, bands)
    else:
        shutil.copyfile(img_in, img_out)
        return img_out

def MakeQuicklook(path_in, path_out, epsg = None, pixelsize = None, method = gdal.GRA_Average, overwrite = True):
    if check_exist(path_out, ignore=overwrite):
        return 1
    ds_in = gdal.Open(path_in)
    if ds_in is None:
        return 1
    srs_in = get_srs(ds_in)
    if epsg is None:
        srs_out = srs_in
    else:
        srs_out = get_srs(epsg)
    if srs_out.IsGeographic():
        pixelsize = pixelsize / 50000
    if srs_in != srs_out:
        t_raster_base = gdal.AutoCreateWarpedVRT(ds_in, srs_in.ExportToWkt(), srs_out.ExportToWkt())
        x_0, x, x_ang, y_0, y_ang, y = t_raster_base.GetGeoTransform()
        newXcount = int(math.ceil(t_raster_base.RasterXSize * (x / pixelsize)))
        newYcount = abs(int(math.ceil(t_raster_base.RasterYSize * (y / pixelsize))))
    else:
        x_0, x, x_ang, y_0, y_ang, y = ds_in.GetGeoTransform()
        newXcount = int(math.ceil(ds_in.RasterXSize * (x / pixelsize)))
        newYcount = abs(int(math.ceil(ds_in.RasterYSize * (y / pixelsize))))
    options = {
        'dt':       ds_in.GetRasterBand(1).DataType,
        'prj':      srs_out.ExportToWkt(),
        'geotrans': (x_0, pixelsize, x_ang, y_0, y_ang, - pixelsize),
        'bandnum':  ds_in.RasterCount,
        'xsize':    newXcount,
        'ysize':    newYcount,
        'compress': 'DEFLATE',
    }
    # scroll(options)
    if ds_in.RasterCount>0:
        nodata = ds_in.GetRasterBand(1).GetNoDataValue()
        if nodata is not None:
            options['nodata'] = nodata
    ds_out = ds(path_out, options=options, editable=True)
    gdal.ReprojectImage(ds_in, ds_out, None, None, method)
    ds_out = None
    return 0

def RasterInfo(path, bits_limit = 16, cut_bits_limit = False, min_bits_limit = False):
    if os.path.exists(path):
        # os.system('gdalinfo -nomd -stats {}'.format(path).replace('&', '^&'))
        r = gdal.Open(path, cut_bits_limit)
        if r is None:
            raise RazmetkaError('Cannot open raster: ' + path)
        gt = r.GetGeoTransform()
        result = {'x_pix_size': abs(gt[1]), 'y_pix_size': abs(gt[-1]), 'x_pix_count': r.RasterXSize, 'y_pix_count': r.RasterYSize}
        try:
            raise Exception
            arr = r.ReadAsArray()
            arr = arr[arr!=0]
            result['data_min'] = int(np.min(arr))
            result['data_max'] = int(np.max(arr))
            bits_up = 2 ** bits_limit - 1
            if result['data_max'] > bits_up:
                if min_bits_limit:
                    if result['data_max'] < 2 ** min_bits_limit - 1:
                        raise RazmetkaError('Bits lower limit is not reached, delete ' + Name(path))
                result['bits_exceed'] = int(np.sum(arr > bits_up))
                if cut_bits_limit:
                    arr = None
                    for i in range(r.RasterCount):
                        band = r.GetRasterBand(i+1)
                        band_arr = band.ReadAsArray()
                        band_arr[band_arr > bits_up] = bits_up
                        band.WriteArray(band_arr)
                    result['data_max'] = bits_up
                    # print('%s raster data cut to %i' % (Name(path), int(bits_up)))
                    r = None
            else:
                result['bits_exceed'] = ''
        except Exception as e:
            # print('RasterInfo error: {}'.format(e))
            result.update({'data_min': '', 'data_max': '', 'bits_exceed': ''})
        return result
    else:
        raise RazmetkaError('Raster end file not found: ' + path)

# Returns:  1) are both files correct and containing geometry?
#           2) do their CRS match?
#           3) do their extents intersect?
def RasterVectorMatch(raster_path, vector_path):
    ds_in, lyr_in = get_lyr_by_path(vector_path)
    r_srs, r_geom = RasterParams(raster_path)
    if (lyr_in and r_srs) and r_geom:
        v_srs = lyr_in.GetSpatialRef()
        if v_srs:
            # crs_match = r_srs.GetAttrValue('AUTHORITY', 1) == v_srs.GetAttrValue('AUTHORITY', 1)
            crs_match = ds_match(r_srs, v_srs)
            if not crs_match:
                r_geom = changeXY(r_geom)
                # print(r_geom.ExportToWkt(), r_srs.ExportToWkt())
                # coordTrans = osr.CoordinateTransformation(r_srs, v_srs)
                # r_geom.Transform(coordTrans)
                r_geom.AssignSpatialReference(r_srs)
                r_geom.TransformTo(v_srs)
                # print(r_geom.ExportToWkt(), v_srs.ExportToWkt())
            else:
                r_geom = changeXY(r_geom)
            for feat in lyr_in:
                v_geom = feat.GetGeometryRef()
                if v_geom:
                    if r_geom.Intersects(v_geom):
                        return True, crs_match, True
                    else:
                        # print(Name(raster_path), r_geom.ExportToWkt(), v_geom.ExportToWkt())
                        pass
            return True, crs_match, False
    return False, False, False

# Создать растровую маску на основе вектора
def SetMask(img_in, msk_out, vec_in = None, burn = None, filter_nodata = True, overwrite = False):
    if check_exist(msk_out, ignore=overwrite):
        return msk_out
    if vec_in is not None:
        if os.path.exists(vec_in):
            valid, crs_match, intersect = RasterVectorMatch(img_in, vec_in)
            if valid:
                if intersect:
                    crs = get_srs(gdal.Open(img_in))
                    vec_reprojected = tempname('shp')
                    vec_to_crs(ogr.Open(vec_in), crs, vec_reprojected)
                    if not os.path.exists(vec_reprojected):
                        vec_reprojected = vec_in
                    # print(vec_reprojected, img_in, msk_out)
                    try:
                        if burn is None:
                            RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, value_colname='gridcode',
                                            filter_nodata=filter_nodata, compress='DEFLATE', overwrite=overwrite)
                        else:
                            RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, burn_value=burn,
                                            filter_nodata=filter_nodata, compress='DEFLATE', overwrite=overwrite)
                        return msk_out
                    except Exception as e:
                        # RasterizeVector(vec_reprojected, img_out, msk_out, data_type=2, value_colname=code_col, value_colname_sec=code_col_sec, compress=compress, overwrite=overwrite)
                        raise RazmetkaError('Masking error: %s %s ' % (img_in, vec_in) + e)
                else:
                    raise RazmetkaError('Raster and vector layers do not intersect: '  + img_in + ' ' + vec_in)
            else:
                raise RazmetkaError('Source invalid: ' + img_in + ' ' + vec_in)
        else:
            RazmetkaError('Mask source not found: ' + vec_in)
    else:
        # Filter nodata doesnt work here
        CreateDataMask(img_in, msk_out, value = burn, nodata = 0, bandnum = 1)
    return msk_out

def MaskInfo(path, replace = {}, shp_path = None):
    raster = gdal.Open(path, bool(replace))
    if raster:
        values = {}
        if not replace:
            replace = {}
        shp_counts = {}
        if shp_path:
            if os.path.exists(shp_path):
                shp_counts = AttrValCalculator(shp_path, attr_id = 'gridcode', replace = replace)
        assert raster.RasterCount == 1
        band = raster.GetRasterBand(1)
        arr_ = band.ReadAsArray()
        mask_keys, mask_counts = np.unique(arr_, return_counts = True)
        for i, key in enumerate(mask_keys):
            if key in replace:
                arr_[arr_ == key] = replace[key]
                key = replace[key]
            if key:
                values[int(key)] = {'msk_pixel_count': int(mask_counts[i])}
                if key in shp_counts:
                    values[key]['msk_feature_count'] = int(shp_counts[key])
        if replace:
            band.WriteArray(arr_)
            raster = None
        return values
    else:
        raise RazmetkaError('Cannot open mask file: ' + path)

def ValuesCountReport(report):
    values = {}
    legend = globals()['legend']
    for id in report:
        msk_info = report[id].get('msk_info', {})
        for val in msk_info:
            if val in values:
                values[val]['msk_pixel_count'] += msk_info[val]['msk_pixel_count']
                values[val]['scene_count'] += 1
            else:
                values[val] = {'msk_pixel_count': msk_info[val]['msk_pixel_count'],
                               'legend': legend.get(val, {}).get('Описание', 'UNKNOWN'),
                               'scene_count': 1}
            if 'msk_feature_count' in msk_info[val]:
                if 'msk_feature_count' in values[val]:
                    values[val]['msk_feature_count'] += msk_info[val]['msk_feature_count']
                else:
                    values[val]['msk_feature_count'] = msk_info[val]['msk_feature_count']
    return values

def AttrValCalculator(shp_in, attr_id = None, replace = {}):
    ds_in, lyr_in = get_lyr_by_path(shp_in)
    counts = {}
    if lyr_in:
        for feat in lyr_in:
            try:
                val = feat.GetField(attr_id)
            except KeyError:
                continue
            if val:
                if val in replace:
                    val = replace[val]
                if val in counts:
                    counts[val] += 1
                else:
                    counts[val] = 1
    return counts

def GetLegend(keys, legend_dict):
    legend = OrderedDict()
    keys.sort()
    for key in keys:
        legend[key] = legend_dict.get(key, {}).get('Описание', 'UNKNOWN')
    return legend

def GetBitsLimit(name):
    if 'KANOPUS' in name:
        return 12
    elif '-KV' in name:
        return 12
    elif 'GEOTON' in name:
        return 10
    elif '-RP' in name:
        return 10
    elif 'KSHMSA' in name:
        return 12
    elif 'KMSS' in name:
        return 8
    else:
        return 16

def ImageMaskCheck(img, msk):
    img_raster = gdal.Open(img)
    msk_raster = gdal.Open(msk)
    if img_raster and msk_raster:
        if (img_raster.RasterXSize != msk_raster.RasterXSize) or (img_raster.RasterYSize != msk_raster.RasterYSize):
            print('Raster size mismatch: ' + Name(img))
        # elif not ds_match(img_raster, msk_raster):
            # print('Projection mismatch: ' + Name(img))
        else:
            return True
    return False

def Report(folder, replace = None, bits_limit = None, cut_bits_limit = False):
    report = OrderedDict()
    for xls in folder_paths(folder, 1, 'xls'):
        if not (('report_fin' in xls) or xls.endswith(r'mask_values_count.xls')):
            report.update(xls_to_dict(xls))
    if bits_limit is not None:
        bits = bits_limit
    for img in folder_paths(folder + '\\images', 1, 'tif'):
        id = Name(img)
        if bits_limit is None:
            bits = GetBitsLimit(id)
        id_img_report = RasterInfo(img, bits_limit = bits, cut_bits_limit = cut_bits_limit)
        if id in report:
            report[id].update(id_img_report)
        else:
            report[id] = id_img_report
        report[id]['img_out'] = img[len(folder):]
    # vec_out = folder_paths(folder + '\\vector', 1, 'shp')
    for msk in folder_paths(folder + '\\masks', 1, 'tif'):
        id = Name(msk)
        if id in report:
            report[id]['matrix_check'] = ImageMaskCheck(folder + report[id]['img_out'], msk)
            # print(id, report[id]['matrix_check'])
            shp_path = r'{}\vector\{}.shp'.format(folder, id)
            if report[id]['matrix_check']:
                report[id]['msk_out'] = msk[len(folder):]
                id_msk_report = MaskInfo(msk, replace = replace, shp_path = shp_path)
                report[id]['msk_info'] = id_msk_report
                msk_values = flist(id_msk_report.keys(), str)
                msk_values.sort()
                report[id]['msk_values'] = ' '.join(msk_values)
            # else:
                # delete(msk)
                # delshp(shp_path)
        else:
            print('UNKNOWN MASK ID: ' + id)
    # scroll(report)
    report_path = folder + '\\report_fin.xls'
    if os.path.exists(report_path):
        os.remove(report_path)
    dict_to_xls(report_path, report, col_list=globals()['report_col_order'])
    values_count = ValuesCountReport(report)
    # scroll(values_count)
    dict_to_xls(folder + '\\mask_values_count.xls', values_count, ['scene_count', 'msk_pixel_count', 'msk_feature_count', 'legend'])
    values_legend = GetLegend(list(values_count), globals()['legend'])
    dict_to_csv(folder + '\\mask_values.csv', values_legend)
    check_folder = folder + '\\check'
    if os.path.exists(check_folder):
        check_imgs = folder_paths(folder + '\\check', 1, 'tif')
        if check_imgs:
            for img_check in check_imgs:
                RasterInfo(img_check, bits_limit = bits, cut_bits_limit = cut_bits_limit)

class RazmetkaError(Exception):

    def __init__(self, *args, **kwargs):
        pass

class RazmetkaDuplicateIdError(Exception):

    def __init__(self, *args, **kwargs):
        pass

class FileList(list):

    def __init__(self, list):
        self.names = []
        for file in self:
            self.names.append(Name(file))

    def PopName(self, name):
        if name in self.names:
            export = self.pop(self.names.index(name))
            self.names.pop(name)
            return export

class DataFolder:

    def __init__(self, corner):
        if os.path.exists(corner):
            self.corner = corner
        else:
            raise FileNotFoundError(corner)

    def DataFolder(self, bandt = 'MS', type = 'img', category = '', ql = False, ms_cut = False, cut = False, create_folder = False):
        band_folder = r'%s\%s' % (self.corner, bandt)
        CheckFolder(band_folder, create_folder, 'Band folder not found: ')
        data_folder = r'%s\%s' % (band_folder, type)
        CheckFolder(data_folder, create_folder, 'Type folder not found: ')
        short_type = type.split('_')[0]
        if category:
            data_folder = r'%s\%s_%s' % (data_folder, short_type, category)
            CheckFolder(data_folder, create_folder, 'Category folder not found: ')
        if ql:
            data_folder = r'%s\&q%sm' % (data_folder, ql)
            CheckFolder(data_folder, create_folder, 'Quicklook folder not found: ')
        if ms_cut:
            data_folder = r'%s\&MScut_%s' % (data_folder, short_type)
            CheckFolder(data_folder, create_folder, 'MS cut folder not found: ')
        if cut:
            data_folder = r'%s\&cut_%s' % (data_folder, short_type)
            CheckFolder(data_folder, create_folder, 'Cut folder not found: ')
        return data_folder

    def DataFiles(self, bandt = 'MS', type = 'img', category = '', ql = False, ms_cut = False, cut = False, mark = None, ext = 'tif'):
        try:
            data_folder = self.DataFolder(bandt = bandt, type = type, category = category, ql = ql, ms_cut = False, cut = cut)
        except FileNotFoundError as e:
            return None
        return FilesDict(data_folder, ext, mark = mark)

    def CropPanByMS(self, category = '', ql = False, cut = False):
        ms_files = self.DataFiles(bandt = 'MS', type = 'img', category = category, ql = ql, cut = cut, mark = None, ext = 'tif')
        pan_files = self.DataFiles(bandt = 'PAN', type = 'img', category = category, ql = ql, cut = cut, mark = None, ext = 'tif')
        if not pan_files:
            raise RazmetkaError('PAN data not found: ' + category)
        if ms_files:
            ms_cut_folder = self.DataFolder(bandt = 'MS', type = 'shp', category = category, ql = ql, ms_cut = True, cut = cut, create_folder = True)
            pan_cut_folder = self.DataFolder(bandt = 'PAN', type='img', category = category, ql = ql, ms_cut = True, cut = cut, create_folder = True)
            for ms_name in ms_files:
                pan_name = ms_name.replace('.MS', '.PAN')
                assert pan_name != ms_name
                if pan_name in pan_files:
                    pan_file = pan_files[pan_name]
                    ms_file = ms_files[ms_name]
                    ms_cut_file = fullpath(ms_cut_folder, ms_name + '_border.shp')
                    VectorizeBand((ms_file, 1), ms_cut_file, classify_table=[(0, None, 1)], index_id='CLASS')
                    if os.path.exists(ms_cut_file):
                        pan_cut_file = fullpath(pan_cut_folder, pan_name + '_MScut.tif')
                        clip_raster(pan_file, ms_cut_file, export_path = pan_cut_file, byfeatures = True, exclude = False, nodata = 0,
                                    path2newshp = None, compress = 'DEFLATE', overwrite = False)
                        print('Written: ' + pan_name + '_MScut.tif')
                    else:
                        print('MS cover not created: ' + ms_name)
                else:
                    print('PAN file not found: ' + pan_name)

    def AlighToMS(self, category = ''):
        ms_files = self.DataFiles(bandt='MS', type='img', category=category, ext='tif')
        pan_files = self.DataFiles(bandt='PAN', type='img', category=category, ext='tif')
        if not pan_files:
            raise RazmetkaError('PAN data not found: ' + category)
        if ms_files:
            pan_folder = self.DataFolder(bandt = 'PAN', type='img', category = category)
            pan_orig_ref_folder = pan_folder + r'\#ref_original'
            suredir(pan_orig_ref_folder)
            for ms_name in ms_files:
                pan_name = ms_name.replace('.MS', '.PAN')
                assert pan_name != ms_name
                if pan_name in pan_files:
                    pan_file = pan_files[pan_name]
                    ms_file = ms_files[ms_name]
                    pan_temp_file = fullpath(pan_folder, pan_name + '.REF.tif')
                    pan_orig_ref_file = fullpath(pan_orig_ref_folder, pan_name, 'tif')
                    RasterAlign(pan_file, ms_file, pan_temp_file, tempdir=None, align_file=None, reproject_method=gdal.GRA_NearestNeighbour)
                    if os.path.exists(pan_temp_file):
                        try:
                            shutil.copyfile(pan_temp_file, pan_orig_ref_file)
                        except:
                            print('Cannot copy file: ' + pan_orig_ref_file)
                        else:
                            os.remove(pan_file)
                            os.rename(pan_temp_file, pan_file)
                            print('Aligned: ' + pan_name)
                else:
                    print('PAN file not found: ' + pan_name)

class Razmetka:

    def __init__(self, mask_type = 'full', band_type = 'MS', vec_type = 'shp_hand', quicklook_size = None):
        self.maskt = mask_type
        self.bandt = band_type
        self.vect = vec_type
        self.qlsize = quicklook_size
        self.input = OrderedDict()
        self.check = {}
        self.sets = []
        self.errors = []

    def AddScene(self, img_in, vec_in, bands, burn, filter_nodata, id_mark = '', appendix_id = ''):
        scene = SceneRazmetka(img_in, vec_in = vec_in, bands = bands, burn = burn, filter_nodata = filter_nodata, id_mark = id_mark + appendix_id)
        if scene:
            if scene.id in self.input:
                self.errors.append('ID duplicate: ' + scene.id)
            else:
                self.input[scene.id] = scene
                return 1
        return 0

    def AddScenes(self, img_in, vec_in, bands, burn, filter_nodata, id_mark = '', by_bands = False):
        if by_bands:
            band_str = globals()['sattelites'].get(GetSattelite(Name(img_in)), {}).get('BANDS')
            if band_str is None:
                raise RazmetkaError('Cannot extract bands for ' + scene.id)
            else:
                count = 0
                band_list = band_str.split(',')
                for i, band in enumerate(band_list):
                    band_id_mark = globals()['bands'].get(band, {}).get('short_name')
                    if band_id_mark is None:
                        raise RazmetkaError('Cannot extract band id mark ' + band + ' for ' + scene.id)
                    elif id_mark:
                        band_id_mark = id_mark + ' ' + band_id_mark
                    scene = SceneRazmetka(img_in, vec_in=vec_in, bands=bands, burn=burn, filter_nodata=filter_nodata,
                                          id_mark=id_mark)
                    count += AddScene(self, img_in, vec_in, [i+1], burn, filter_nodata, id_mark = band_id_mark)
                return count
        else:
            return AddScene(self, img_in, vec_in, bands, burn, filter_nodata, id_mark = id_mark)

    def CreateQuicklooks(self, corner, category, type = 'img', overwrite = False):
        assert isinstance(self.qlsize, int)
        data = DataFolder(corner)
        ql_files = data.DataFiles(bandt = self.bandt, type = type, category = category, ql = self.qlsize, ext='tif')
        img_files = data.DataFiles(bandt = self.bandt, type = type, category = category, ext = 'tif')
        if ql_files:
            if len(ql_files) == len(img_files):
                return None
        if img_files:
            ql_folder = data.DataFolder(bandt = 'MS', type = type, category = category, ql = self.qlsize, cut = False, create_folder = True)
            bar = IncrementalBar('Идёт создание квиклуков: ', max=len(img_files))
            for id in img_files:
                path_out = fullpath(ql_folder, id + '_%im.tif' % self.qlsize)
                MakeQuicklook(img_files[id], path_out, epsg = None, pixelsize = self.qlsize, method = gdal.GRA_Average, overwrite = overwrite)
                bar.next()
        else:
            print('Image files not found for ' + category)

    def GetCutBorders(self, corner, category, type):
        data = DataFolder(corner)
        cut_img_files = data.DataFiles(bandt = self.bandt, type = type, category = category, cut = 1, ext = 'tif')
        if cut_img_files:
            cut_shp_folder = data.DataFolder(bandt = self.bandt, type = type, category = category) + '\\&cut_shp'
            suredir(cut_shp_folder)
            cut_shp_files = FilesDict(cut_shp_folder, 'shp')
            for cut_id in cut_img_files:
                # cut_id = Name(img)
                if cut_id in cut_shp_files:
                    continue
                else:
                    ql = fullpath(cut_shp_folder, cut_id, 'shp')
                    VectorizeBand((cut_img_files[cut_id], 1), ql, classify_table = [(0, None, 1)], index_id = 'CLASS')
                    cut_shp_files[cut_id] = ql
            return cut_shp_files

    def CutQuicklooks(self, corner, category, type = 'img', overwrite = False):
        assert isinstance(self.qlsize, int)
        data = DataFolder(corner)
        ql_files = data.DataFiles(bandt=self.bandt, type = type, category = category, ql = self.qlsize, ext = 'tif')
        cut_shp_files = self.GetCutBorders(corner, category, type)
        # scroll([cut_shp_files.keys(), ql_files])
        if ql_files and cut_shp_files:
            ql_cut_img_folder = data.DataFolder(bandt = self.bandt, type = type, category = category, ql = self.qlsize, cut = 1, create_folder = 1)
            for cut_id in cut_shp_files:
                id, cut_num = cut_id.split('_cut')
                for ql_id in ql_files:
                    if id in ql_id:
                        ql_cut_img = fullpath(ql_cut_img_folder, ql_id + '_cut' + cut_num, 'tif')
                        # print(ql_cut_img)
                        clip_raster(ql_files[ql_id], cut_shp_files[cut_id], export_path = ql_cut_img, compress = 'DEFLATE', overwrite = overwrite)
                        break

    def EnterInput(self, corner, category, bands = None, use_empty = False, use_cut = False, burn = None, filter_nodata = True, by_bands = False, appendix_id = '', allow_corner_vector = True):
        count = 0
        try:
            data = DataFolder(corner)
            img_files = data.DataFiles(bandt = self.bandt, type = 'img', category = category, ql = self.qlsize, cut = use_cut, ext = 'tif')
            # scroll(img_files)
            if img_files is None:
                raise RazmetkaError('Image files not found for: ' + category)
            if use_empty:
                for id in img_files:
                    try:
                        if by_bands:
                            bands_list = GetBandList(id)
                            for band_params in bands_list:
                                try:
                                    bands, id_mark = band_params
                                    count += int(self.AddScene(img_files[id], None, bands, burn, filter_nodata, id_mark = id_mark, appendix_id = appendix_id))
                                except RazmetkaError as e:
                                    self.errors.append(e)
                        else:
                            count += int(self.AddScene(img_files[id], None, bands, burn, filter_nodata))
                    except RazmetkaError as e:
                        self.errors.append(e)
            else:
                vec_files_tuple = self.GetVectorFilesTuple(data, category, use_cut, by_bands, allow_corner_vector)
                # vec_files = data.DataFiles(bandt = self.bandt, type = self.vect, category = category, ql = self.qlsize, cut = use_cut, ext = 'shp')
                # if allow_corner_vector and (self.qlsize is not None):
                    # corner_vec_files = data.DataFiles(bandt=self.bandt, type=self.vect, category=category, cut=use_cut, ext='shp')
                # if by_bands:
                    # band_vec_files = data.DataFiles(bandt = 'BANDS', type = self.vect, category = category, ql = self.qlsize, cut = use_cut, ext = 'shp')
                    # if allow_corner_vector and (self.qlsize is not None):
                        # band_corner_vec_files = data.DataFiles(bandt = 'BANDS', type = self.vect, category = category, cut = use_cut, ext = 'shp')
                # scroll(vec_files_tuple, print_type=1)
                if not vec_files_tuple:
                    raise RazmetkaError('Vector data not found: ' + corner + ' ' + category)
                for id in img_files:
                    img_file = img_files[id]
                    try:
                        if by_bands:
                            bands_list = GetBandList(id)
                            for band_params in bands_list:
                                try:
                                    bands, id_mark = band_params
                                    vec_file = self.GetVecFile(id + '_' + id_mark, vec_files_tuple, id_mark)
                                    count += int(self.AddScene(img_file, vec_file, bands, burn, filter_nodata, id_mark = id_mark, appendix_id = appendix_id))
                                except RazmetkaError as e:
                                    # if use_cut:
                                        # scroll(vec_files_tuple, header = id, lower = use_cut)
                                        # sys.exit()
                                    self.errors.append(e)
                        else:
                            # vec_file = vec_files.get(id, vec_files.get(id.replace('_{}m'.format(self.qlsize), '')))
                            vec_file = self.GetVecFile(id, vec_files_tuple, appendix_id)
                            if vec_file is None:
                                continue
                            count += int(self.AddScene(img_file, vec_file, bands, burn, filter_nodata, appendix_id = appendix_id))
                    except RazmetkaError as e:
                        self.errors.append(e)
        except RazmetkaError as e:
            print('Error collecting input from {} {}'.format(corner, category) )
            self.errors.append(e)
        else:
            self.sets.append((corner, category, bands, use_empty, use_cut, burn, filter_nodata, count))
        return count

    def GetVectorFilesTuple(self, data, category, use_cut, by_bands, allow_corner_vector):
        vec_files = data.DataFiles(bandt=self.bandt, type=self.vect, category=category, ql=self.qlsize, cut=use_cut, ext='shp')
        if allow_corner_vector and (self.qlsize is not None):
            corner_vec_files = data.DataFiles(bandt=self.bandt, type=self.vect, category=category, cut=use_cut, ext='shp')
        if by_bands:
            band_vec_files = data.DataFiles(bandt='BANDS', type=self.vect, category=category, ql=self.qlsize, cut=use_cut, ext='shp')
            if allow_corner_vector and (self.qlsize is not None):
                band_corner_vec_files = data.DataFiles(bandt='BANDS', type=self.vect, category=category, cut=use_cut, ext='shp')
                return [band_vec_files, band_corner_vec_files, vec_files, corner_vec_files]
            else:
                return [band_vec_files, vec_files]
        else:
            if allow_corner_vector and (self.qlsize is not None):
                return [vec_files, corner_vec_files]
            else:
                return [vec_files]

        vec_files = data.DataFiles(bandt=self.bandt, type=self.vect, category=category, ql=self.qlsize, cut=use_cut, ext='shp')
        if allow_corner_vector and (self.qlsize is not None):
            corner_vec_files = data.DataFiles(bandt=self.bandt, type=self.vect, category=category, cut=use_cut, ext='shp')
        else:
            corner_vec_files = None
        band_corner_vec_files = None
        if by_bands:
            band_vec_files = data.DataFiles(bandt='BANDS', type=self.vect, category=category, ql=self.qlsize, cut=use_cut, ext='shp')
            if allow_corner_vector and (self.qlsize is not None):
                band_corner_vec_files = data.DataFiles(bandt='BANDS', type=self.vect, category=category, cut=use_cut, ext='shp')
                return (band_vec_files, band_corner_vec_files, vec_files, corner_vec_files)
            else:
                return (band_vec_files, vec_files)
        else:
            return (corner_vec_files, vec_files)

    def GetVecFile(self, id, vec_files_tuple, id_mark):
        for vec_files in vec_files_tuple:
            if vec_files:
                for part in ['', '_{}m'.format(self.qlsize), '_{}'.format(id_mark), '_{}m_{}'.format(self.qlsize, id_mark)]:
                    id_check = id.replace(part, '')
                    vec_file = vec_files.get(id_check, '')
                    if vec_file:
                        return vec_file
                id_check = id.replace('_{}m'.format(self.qlsize), '').replace('_{}'.format(id_mark), '')
                vec_file = vec_files.get(id_check, '')
                if vec_file:
                    return vec_file
        # print('Vector file not found: ' + id)
        # for part in ['', '_{}m'.format(self.qlsize), '_{}'.format(id_mark), '_{}m_{}'.format(self.qlsize, id_mark)]:
            # print(id.replace(part, ''))
        raise RazmetkaError('Vector file not found: ' + id)

    def EnterCheck(self, corner, category, bands = None, use_cut = False, by_bands = False, appendix_id = ''):
        count = 0
        try:
            data = DataFolder(corner)
            check_files = data.DataFiles(bandt = self.bandt, type = 'img_check', category = category, ql = self.qlsize, cut = use_cut, ext = 'tif')
            cat_check = {}
            if check_files:
                for id in check_files:
                    if bands is None:
                        bands = list(range(1, gdal.Open(check_files[id]).RasterCount + 1))
                    if appendix_id:
                        id_key = id + '_' + appendix_id
                    cat_check[id_key] = (check_files[id], bands, by_bands)
                if cat_check:
                    if category in self.check:
                        self.check[category].update(cat_check)
                    else:
                        self.check[category] = cat_check
        except RazmetkaError as e:
            print('Error collecting controls from {} {}'.format(corner, category) )
            self.errors.append(e)
        return count

    def MakeRazmetka(self, output_folder, replace = None, del_codes = [], cut_bits_limit = False, min_bits_limit = None, filter_mark = None, control_lim = None, overwrite = False):
        if self.input:
            img_folder = output_folder + '\images'
            msk_folder = output_folder + '\masks\\' + self.maskt
            vec_folder = output_folder + r'\vector'
            check_folder = output_folder + r'\check'
            razmetka_report = OrderedDict()
            if filter_mark:
                input_len = KeyMarkedCount(self.input.keys(), filter_mark)
            else:
                input_len = len(self.input)
            bar = IncrementalBar('Идёт создание разметки: ', max = input_len)
            for id in self.input:
                if filter_mark:
                    if not filter_mark in id:
                        continue
                try:
                    scene = self.input[id]
                    # print(id)
                    img = scene.SceneImage(img_folder, overwrite = overwrite)
                    msk = scene.SceneMask(msk_folder, vec_folder = vec_folder, overwrite = overwrite)
                    razmetka_report[id] = scene.SceneReport(img, msk)
                    razmetka_report[id]['msk_info'] = msk_info = MaskInfo(msk, replace = replace, shp_path = None)
                    # scroll(msk_info, header='MSK ' + id)
                    # msk_info = MaskInfo(msk, replace=replace, shp_path=scene.vec)
                    msk_values = list(msk_info.keys())
                    msk_values.sort()
                    razmetka_report[id]['msk_values'] = ' '.join(flist(msk_values, str))
                    for del_code in del_codes:
                        if del_code in msk_values:
                            razmetka_report.pop(id)
                            scene.ClearMask(img_folder, msk_folder, vec_folder = vec_folder)
                            self.errors.append('Deleted ID: ' + id)
                except RazmetkaError as e:
                    if e.startswith('Bits lower limit is not reached'):
                        scene.ClearMask(img_folder, msk_folder, vec_folder = vec_folder)
                    self.errors.append('{}: {}'.format(id, e))
                # except Exception as e:
                # self.errors.append('{}: {}'.format(id, e))
                finally:
                    bar.next()
            for cat in self.check:
                try:
                    cat_files = self.check[cat]
                    cat_folder = fullpath(check_folder, cat)
                    suredir(cat_folder)
                    for i, id_check in enumerate(cat_files):
                        if control_lim is not None:
                            if i >= control_lim:
                                continue
                        img_check, bands, by_bands = cat_files[id_check]
                        img_out = fullpath(cat_folder, id_check, 'tif')
                        SetImage(img_check, img_out, bands, overwrite = overwrite)
                except Exception as e:
                    self.errors.append('Check image copying error: ' + e)
            # scroll(razmetka_report)
            report_path = r'{}\report_{}.xls'.format(output_folder, str(datetime.now()).replace(' ','_').replace(':','-')[:19])
            dict_to_xls(report_path, razmetka_report, col_list = globals()['report_col_order'])
        else:
            print('Input is empty, cannot make razmetka')
        if self.errors:
            scroll(self.errors, header='ERRORS FOUND:')
            with open(output_folder + '\\errors.txt', 'w') as errors_txt:
                errors_txt.write('\n'.join(flist(self.errors, str)))
        Report(output_folder, replace=replace, cut_bits_limit=cut_bits_limit)

class SceneRazmetka:

    def __init__(self, img_in, vec_in = None, bands = None, burn = None, filter_nodata = True, id_mark = ''):
        self.id = Name(img_in)
        self.sat = GetSattelite(self.id)
        if id_mark:
            self.id = self.id + '_' + id_mark
        if vec_in is None:
            if burn is None:
                raise RazmetkaError('Pairing error ' + self.id)
            self.vec = None
        elif not os.path.exists(vec_in):
            raise RazmetkaError('Vector error: ' + vec_in)
        if not os.path.exists(img_in):
            raise RazmetkaError('Image error: ' + img_in)
        self.img = img_in
        self.AppendBands(bands)
        self.burn = burn
        self.vec = vec_in
        self.filter_nodata = filter_nodata

    def __str__(self):
        return '{}\n  IMG\t{}\n  VEC\t{}\n  SAT\t{}\n  BANDS\t{}\n  BURN\t{}\n  ~NOD\t{}\n'.format(
            self.id, self.img, self.vec, self.sat, ' '.join(flist(self.bands, str)), self.burn, self.filter_nodata)

    def AppendBands(self, bands):
        img = gdal.Open(self.img)
        img_bands = list(range(1, img.RasterCount + 1))

        if img:
            if bands is None:
                self.bands = img_bands
            elif isinstance(bands, (type([]), type({}))):
                d = isinstance(bands, dict)
                for key in bands:
                    if not int(key) in img_bands:
                        print('Bands error: ' + str(bands) + ' ' + self.img)
                        raise RazmetkaError('Bands error: ' + str(bands) + ' ' + self.img)
                    elif d:
                        try:
                            float(bands[key])
                        except:
                            print('Bands multiply error: ' + str(bands) + ' ' + self.img)
                            raise RazmetkaError('Bands multiply error: ' + str(bands) + ' ' + self.img)
                self.bands = bands
            else:
                print('Bands type error: ' + str(bands) + ' ' + self.img)
                raise RazmetkaError('Bands type error: ' + str(bands) + ' ' + self.img)
        else:
            raise RazmetkaError('Image error: ' + self.img)

    def SceneImage(self, img_folder, overwrite = False):
        img_out = r'{}\{}\{}.tif'.format(img_folder, self.sat, self.id)
        suredir(os.path.split(img_out)[0])
        return SetImage(self.img, img_out, self.bands, overwrite = overwrite)

    def SceneMask(self, msk_folder, vec_folder = None, overwrite = False):
        msk_out = r'{}\{}\{}.tif'.format(msk_folder, self.sat, self.id)
        f, n, e = split3(msk_out)
        suredir(f)
        if self.vec and vec_folder:
            suredir(vec_folder)
            copyshp(self.vec, vec_folder, final_name = n)
        return SetMask(self.img, msk_out, vec_in = self.vec, burn = self.burn, filter_nodata = self.filter_nodata, overwrite = overwrite)

    def ClearMask(self, img_folder, msk_folder, vec_folder = None):
        delete(r'{}\{}\{}.tif'.format(img_folder, self.sat, self.id))
        delete(r'{}\{}\{}.tif'.format(msk_folder, self.sat, self.id))
        if vec_folder:
            for file in folder_paths(vec_folder, 1):
                if Name(file) == self.id:
                    delete(file)
            # driver = ogr.GetDriverByName('ESRI Shapefile')
            # driver.DeleteDataSource(r'{}\{}.shp'.format(msk_folder, self.id))

    def SceneReport(self, img_out, msk_out):
        report = {'img_in': self.img, 'img_out': img_out, 'msk_out': msk_out}
        if self.vec:
            report['vec_in'] = self.vec
        report.update(RasterInfo(img_out))
        return report