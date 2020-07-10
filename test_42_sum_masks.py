from geodata import *

def collect_masks(dir_in):
    report = OrderedDict()
    for file in folder_paths(dir_in,1,'tif'):
        f,n,e = split3(file)
        id = n[4:]
        if id in report:
            report[id].append(file)
        else:
            report[id] = [file]
    return report

def repack(path_dict, path_out):
    new_paths = OrderedDict()
    for key in path_dict:
        f = fullpath(path_out, key)
        suredir(f)
        new_paths[key] = []
        for file in path_dict[key]:
            new = fullpath(f, os.path.basename(file))
            shutil.move(file, new)
            new_paths[key].append(new)
    return new_paths

def order(l, order):
    report = []
    for key in order:
        for i, val in enumerate(l):
            if key in val:
                report.append(l.pop(i))
    return report

def sum_rasters(path_list, path_out, order_keys=(), overwrite=True):
    if check_exist(path_out, overwrite):
        return 1
    path_list = obj2list(path_list)
    path_list = order(path_list, order_keys)
    if len(path_list) > 0:
        din = gdal.Open(path_list[0])
        raster_array = din.GetRasterBand(1).ReadAsArray()
        if len(path_list) > 1:
            bandpaths = []
            for path in path_list[1:]:
                bandpaths.append((path, 1))
            data = MultiRasterData(bandpaths, data=2)
            for arr_ in data:
                mask = raster_array==0
                raster_array[mask] += arr_[mask]
    else:
        return 1
    dout = ds(path_out, copypath=path_list[0], options={'bandnum': 1, 'compress': 'DEFLATE'}, editable=True)
    dout.GetRasterBand(1).WriteArray(raster_array)
    dout = None
    return 0

dir_in = r'e:\test\razmetka\data\set022'
dir_out = r'd:\terratech\razmetka\set022__20200702__doobuchenie_MWT_MGR_MQR_MCN_MBD_PMS\masks\full\kanopus'

suredir(dir_out)

path_dict = collect_masks(dir_in)
# path_dict = repack(path_dict, dir_in)

for i, id in enumerate(path_dict):
    # scroll(path_dict[id])
    try:
        sum_rasters(path_dict[id], r'%s\MSK-%s.tif' % (dir_out, id),
                    order_keys=('MQR-', 'MGR-', 'MCN-', 'MWT-', 'MBD-'), overwrite=False)
        print('%i %s' % (i+1, id))
    except:
        print('%i -- ERROR -- %s' % (i+1, id))

