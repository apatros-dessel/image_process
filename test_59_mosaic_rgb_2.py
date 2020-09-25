from image_processor import process
from geodata import *

pin = r'd:\digital_earth\planet_20200920\clip_fire_madashenskoye_2019aug8_PSScene4Band_7824956a-a67d-4633-8535-d9e76ec4a09c'
pout = r'd:\digital_earth\planet_20200920\2019-08-08_v3\Madashenskoe_20190808_rgb_v3.tif'
tmpts = [#'KV.+KANOPUS',
         '_.{4}_.+AnalyticMS_clip',
        ]

def GetRasterPercentileUInteger(files, min_p = 0.02, max_p = 0.98, bands = [1,2,3], nodata = 0, max = 65536, manage_clouds = False):
    max = int(max)
    count = np.zeros((len(bands), max), np.uint64)
    sums = np.zeros((len(bands)),int)
    for file in files:
        raster = gdal.Open(file)
        if raster:
            if manage_clouds:
                f,n,e = split3(file)
                proc = process().input(f)
                for ascene in proc.scenes:
                    if file==ascene.get_raster_path('Analytic'):
                        clouds = float(get_from_tree(ascene.meta.container.get('xmltree'), 'cloudCoverPercentage')[0]) / 100.0
            for i, band in enumerate(bands):
                values, numbers = np.unique(raster.GetRasterBand(band).ReadAsArray(), return_counts=True)
                nodatamatch = np.where(values==nodata)
                if len(nodatamatch)>0:
                    for val in nodatamatch:
                        numbers[val] = 0
                sum = np.sum(numbers)
                if manage_clouds and (clouds>0):
                    nocloud_sum = int(sum * (1 - clouds))
                    sum_ = 0
                    sums[i] += nocloud_sum
                else:
                    clouds = False
                    sums[i] += sum
                for val, num in zip(values, numbers):
                    if clouds:
                        sum_ += num
                        if sum_ >= nocloud_sum:
                            count[i, val] += num - sum_ + nocloud_sum
                            break
                    count[i, val] += num
                del values
                del numbers
    result = []
    for sum, hystogram in zip(sums, count):
        min_num = sum*min_p
        max_num = sum*max_p
        cur_min_sum = 0
        for i, num in enumerate(hystogram):
            cur_min_sum += num
            if cur_min_sum < min_num:
                continue
            else:
                min_val = i
                break
        cur_max_sum = sum
        for i, num in enumerate(hystogram[::-1]):
            cur_max_sum -= num
            if cur_max_sum > max_num:
                continue
            else:
                max_val = max - i
                break
        result.append((min_val, max_val))
    return result

def group_files(files, tmpts):
    groups = {}
    for file in files:
        f,n,e = split3(file)
        for tmpt in tmpts:
            file_id = re.search(tmpt, n)
            if file_id:
                file_id = file_id.group()
                if file_id in groups:
                    groups[file_id].append(file)
                else:
                    groups[file_id] = [file]
                break
    return groups

t = datetime.now()
files = folder_paths(pin,1,'tif')
groups = group_files(files, tmpts)
folder_out = os.path.dirname(pout)

suredir(folder_out)
mosaic_list = []
for group in groups.values():
    params = GetRasterPercentileUInteger(group, 0.01, 0.998, manage_clouds=True)
    print(params)
    for file in group:
        f,n,e = split3(file)
        rgb = n+'.RGB'
        rgb_out = fullpath(folder_out, rgb, e)
        RasterToImage3(file, rgb_out, method=3, band_limits=params, alpha=True, compress='DEFLATE', gamma=(0.80, 0.80, 0.85),
                       enforce_nodata=0, overwrite=False)
        print('File written: %s' % rgb)
        mosaic_list.append(rgb_out)

print('FINISHED RGB FOR: {}'.format(datetime.now()-t))

Mosaic(mosaic_list, pout, band_num=3, options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'BIGTIFF=YES', 'NUM_THREADS=ALL_CPUS'])

print('FINISHED MOSAIC FOR: {}'.format(datetime.now()-t))

