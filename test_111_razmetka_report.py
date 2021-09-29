from geodata import *

folders = FolderDirs(r'd:\rks\razmetka').values()
# folders = [r'e:\rks\razmetka\!set038__20201218__water_landsat']

meta_folder = r'\\172.21.195.2\thematic\Sadkov_SA\code\razmetka_params'
sattelites = xls_to_dict(fullpath(meta_folder, 'sattelites.xls'))
legend = xls_to_dict(fullpath(meta_folder, 'legend.xls'))
report_col_order = ['r', 'v', 'img_out', 'msk_out', 'x_pix_count', 'y_pix_count', 'x_pix_size', 'y_pix_size',
                        'data_min', 'data_max', 'bits_exceed', 'msk_values']

class RazmetkaError(Exception):

    def __init__(self, *args, **kwargs):
        pass

def RasterInfo(path, bits_limit = 16):
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
            bits_up = 2 ** bits_limit - 1
            if result['data_max'] > bits_up:
                result['bits_exceed'] = int(np.sum(arr > bits_up))
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

def Report(folder):
    report_path = folder + '\\report_fin.xls'
    if os.path.exists(report_path):
        print('FILE EXISTS: ' + report_path)
        return None
    report = OrderedDict()
    for xls in folder_paths(folder, 1, 'xls', filter_folder=['quicklook']):
        if not (xls.endswith('report_fin.xls') or xls.endswith(r'mask_values_count.xls')):
            report.update(xls_to_dict(xls))
    id_part = ''
    for img in folder_paths(folder + '\\images', 1, 'tif', filter_folder=['quicklook'], empty_return=[]):
        id = Name(img)
        if id.startswith('IM'):
            id_part = id.split('-')[0]
        else:
            id_part = ''
        id_img_report = RasterInfo(img, bits_limit = GetBitsLimit(id))
        if id in report:
            report[id].update(id_img_report)
        else:
            report[id] = id_img_report
        report[id]['img_out'] = img[len(folder):]
    for msk in folder_paths(folder + '\\masks', 1, 'tif', filter_folder=['quicklook'], empty_return=[]):
        id = Name(msk)
        if id_part:
            if re.search('^IMCH\d+__', id):
                id = '__'.join([id_part] + id.split('__')[1:])
            else:
                id = '-'.join([id_part] + id.split('-')[1:])
        if id in report:
            report[id]['msk_out'] = msk[len(folder):]
            id_msk_report = MaskInfo(msk, replace={})
            report[id]['msk_info'] = id_msk_report
            msk_values = flist(id_msk_report.keys(), str)
            msk_values.sort()
            report[id]['msk_values'] = ' '.join(msk_values)
        else:
            print('UNKNOWN MASK ID: ' + id)
    if report:
        if os.path.exists(report_path):
            os.remove(report_path)
        dict_to_xls(report_path, report, col_list=globals()['report_col_order'])
        values_count = ValuesCountReport(report)
        dict_to_xls(folder + '\\mask_values_count.xls', values_count, ['scene_count', 'msk_pixel_count', 'msk_feature_count', 'legend'])
        values_legend = GetLegend(list(values_count), globals()['legend'])
        dict_to_csv(folder + '\\mask_values.csv', values_legend)

for folder in folders:
    if 'kanopus' in folder.lower():
        continue
    Report(folder)
    print('FINISHED: ' + os.path.split(folder)[1])