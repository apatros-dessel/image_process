from geodata import *

meta_folder = r'\\172.21.195.2\thematic\Sadkov_SA\code\razmetka_params'

sattelites = xls_to_dict(fullpath(meta_folder, 'sattelites.xls'))
legend = xls_to_dict(fullpath(meta_folder, 'legend.xls'))

corner_list = [
    r'd:\rks\razmetka\sentinel_sentinel_new',
    r'\\172.21.195.2\thematic\Sarychev_EU\sentinel\set006__20201224__sentinel_sentinel_difficult_winter',
    r'\\172.21.195.2\thematic\Sarychev_EU\sentinel\set005__20201224__sentinel_sentinel_difficult_clouds',
    r'd:\rks\razmetka\set001__20200408__sentinel_time_composit_tver__fix001',
    r'd:\rks\razmetka\set002__20200618__sentinel_kanopus_time_composit',
    r'd:\rks\razmetka\set004__20201111__sentinel_change__fix001',
]
out_folder = r'd:\rks\razmetka\set009__20210926__sentinel_sentinel_change_new'
sat = 'sentinel-sentinel'
type = 'change'
report_col_order = ['r', 'v', 'img_out', 'msk_out', 'x_pix_count', 'y_pix_count', 'x_pix_size', 'y_pix_size',
                        'data_min', 'data_max', 'bits_exceed', 'msk_values']

class RazmetkaError(Exception):

    def __init__(self, *args, **kwargs):
        pass

def PairImgMsk(img_folder, msk_folder):
    pairs = {}
    for img in folder_paths(img_folder, 1, 'tif', filter_folder=['sentinel_kanopus']):
        id = Name(img)
        if id.startswith('IMCH8'):
            pairs[id] = { 'img': img }
    for msk in folder_paths(msk_folder, 1, 'tif'):
        id = Name(msk)
        if not id in pairs:
            id = 'IMCH8' + id.lstrip('MCHD8')
        if not id in pairs:
            print('MISSED: ' + id)
        else:
            pairs[id]['msk'] = msk
    return pairs

def CheckImage(img_in, bands):
    raster = gdal.Open(img_in)
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
        repair, counter = CheckImage(img_out, range(1, len(bands)+1))
        if not (repair or overwrite):
            print('ORIGINAL ' + Name(img_out))
            return img_out
    if os.path.exists(img_in):
        repair, counter = CheckImage(img_in, bands)
    else:
        raise FileNotFoundError(img_in)
    if repair:
        print('REPAIRED ' + Name(img_out))
        return RepairImage(img_in, img_out, bands)
    else:
        shutil.copyfile(img_in, img_out)
        print('COPY ' + Name(img_out))
        return img_out

def RasterInfo(path):
    if os.path.exists(path):
        # os.system('gdalinfo -nomd -stats {}'.format(path).replace('&', '^&'))
        r = gdal.Open(path)
        if r is None:
            raise RazmetkaError('Cannot open raster: ' + path)
        gt = r.GetGeoTransform()
        result = {'x_pix_size': abs(gt[1]), 'y_pix_size': abs(gt[-1]), 'x_pix_count': r.RasterXSize, 'y_pix_count': r.RasterYSize}
        try:
            arr = r.ReadAsArray()
            arr = arr[arr!=0]
            result['data_min'] = int(np.min(arr))
            result['data_max'] = int(np.max(arr))
            if result['data_max'] > 1023:
                result['bits_exceed'] = int(np.sum(arr > 1023))
            else:
                result['bits_exceed'] = ''
        except Exception as e:
            print(e)
            result.update({'data_min': '', 'data_max': '', 'bits_exceed': ''})
        return result
    else:
        raise RazmetkaError('Raster end file not found: ' + path)

def MaskInfo(path, replace = {}, shp_path = None):
    raster = gdal.Open(path, bool(replace))
    if raster:
        values = {}
        if replace and shp_path:
            shp_counts = AttrValCalculator(shp_in, 'gridcode')
        else:
            shp_counts = {}
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

def GetLegend(keys, legend_dict):
    legend = OrderedDict()
    keys.sort()
    for key in keys:
        legend[key] = legend_dict.get(key, {}).get('Описание', 'UNKNOWN')
    return legend

def Report(folder):
    report = OrderedDict()
    for xls in folder_paths(folder, 1, 'xls', filter_folder=['quicklook']):
        if not (xls.endswith('report_fin.xls') or xls.endswith(r'mask_values_count.xls')):
            report.update(xls_to_dict(xls))
    for img in folder_paths(folder + '\\images', 1, 'tif', filter_folder=['quicklook']):
        id = Name(img)
        id_img_report = RasterInfo(img)
        if id in report:
            report[id].update(id_img_report)
        else:
            report[id] = id_img_report
        report[id]['img_out'] = img[len(folder):]
    for msk in folder_paths(folder + '\\masks', 1, 'tif', filter_folder=['quicklook']):
        id = Name(msk)
        if id in report:
            report[id]['msk_out'] = msk[len(folder):]
            id_msk_report = MaskInfo(msk, replace={})
            report[id]['msk_info'] = id_msk_report
            msk_values = flist(id_msk_report.keys(), str)
            msk_values.sort()
            report[id]['msk_values'] = ' '.join(msk_values)
        else:
            print('UNKNOWN MASK ID: ' + id)
    report_path = folder + '\\report_fin.xls'
    if os.path.exists(report_path):
        os.remove(report_path)
    dict_to_xls(report_path, report, col_list=globals()['report_col_order'])
    values_count = ValuesCountReport(report)
    dict_to_xls(folder + '\\mask_values_count.xls', values_count, ['scene_count', 'msk_pixel_count', 'msk_feature_count', 'legend'])
    values_legend = GetLegend(list(values_count), globals()['legend'])
    dict_to_csv(folder + '\\mask_values.csv', values_legend)

for corner in corner_list:

    img_folder = corner + '\\images'
    msk_folder = corner + '\\masks'
    pairs = PairImgMsk(img_folder, msk_folder)
    out_img_folder = r'%s\images\%s' % (out_folder, sat)
    out_msk_folder = r'%s\masks\%s\%s' % (out_folder, type, sat)
    suredir(out_img_folder)
    suredir(out_msk_folder)

    for id in pairs:
        SetImage(pairs[id]['img'], fullpath(out_img_folder, id, 'tif'), [1,2,3,4,5,6,7,8])
        if pairs[id].get('msk'):
            SetImage(pairs[id]['msk'], fullpath(out_msk_folder, id, 'tif'), [1])
        print(id)

    if folder_paths(corner, 1, 'xls'):
        for xls in folder_paths(corner, 1, 'xls'):
            copyfile(xls, fullpath(out_folder, os.path.split(xls)[1]))

Report(out_folder)
