from geodata import *

paths_in_txt = r'd:\digital_earth\RSP_Simferopol\copy_paths.txt'
paths_out_txt = r'd:\digital_earth\RSP_Simferopol\parsed_paths.txt'
out_dir = r'd:\digital_earth\RSP_Simferopol'

rsp_source_tmpt = r'.*RP.+PMS.L2[^\.]*$'
rsp_grn_tmpt = r'RP.+PMS.L2\..{0,3}\d{8}$'
rsp_rgb_tmpt = r'.*RP.+PMS.L2\..*\d*\.?RGB$'
rsp_ql_tmpt = r'.*RP.+PMS.L2\..*\.?QL$'
rsp_id_tmpt = r'RP.+PMS.L2'

def copymove(file_in, file_out, preserve_original):
    if file_in==file_out:
        print('ERROR: IN AND OUT PATHS ARE THE SAME')
    elif not os.path.exists(file_in):
        print('FILE NOT FOUND: %s' % file_in)
    elif os.path.exists(file_out):
        print('FILE ALREADY EXISTS: %s' % file_out)
    elif preserve_original:
        shutil.copyfile(file_in, file_out)
    else:
        shutil.move(file_in, file_out)

def PrintFiles(id, files_dict):
    sour_line = '\n  SOURCE:\n    ' * bool(files_dict['SOUR']) + '\n    '.join(files_dict['SOUR'])
    grn_line = '\n  GRANULES:\n    ' * bool(files_dict['GRN']) + '\n    '.join(files_dict['GRN'])
    rgb_line = '\n  RGB:\n    ' * bool(files_dict['RGB']) + '\n    '.join(files_dict['RGB'])
    ql_line = '\n  QUICKLOOK:\n    ' * bool(files_dict['QL']) + '\n  '.join(files_dict['QL'])
    fin = 'ID: ' + ''.join([id, sour_line, grn_line, rgb_line, ql_line])
    return fin

def GetGranuleId(name, tmpt):
    search = re.search(tmpt, name)
    if search:
        grn_id = search.group()
        if not 'GRN' in grn_id:
            grn_id = grn_id.replace('L2.','L2.GRN')
        return grn_id

def SortById(files, tmpt):
    sorted = {}
    for file in files:
        f,n,e = split3(file)
        grn_id = GetGranuleId(n, tmpt)
        if grn_id in sorted:
            sorted[grn_id].append(file)
        else:
            sorted[grn_id] = [file]
    return sorted

def CheckRasterParams(file):
    raster = gdal.Open(file)
    if raster:
        size = os.path.getsize(file)
        shape = (raster.RasterCount, raster.RasterXSize, raster.RasterYSize)
        geotransform = raster.GetGeoTransform()
        dtype = raster.GetRasterBand(1).DataType
        return (size, shape, geotransform, dtype)
    else:
        print('Cannot read file: %s' % file)
        return None

def FindPairsInList(files):
    pairs = {}
    for file in files:
        params = CheckRasterParams(file)
        if params:
            size, shape, geotransform, dtype = params
            params = (shape, geotransform, dtype)
            if params in pairs:
                pairs[params].append((file, size))
            else:
                pairs[params] = [(file, size)]
    # if len(pairs)>1:
        # for params in pairs:
            # print('{} {}'.format(params, pairs[params]))
    return pairs

def ChooseMinSize(filesizes):
    file_fin, size_fin = filesizes[0]
    for file, size in filesizes[1:]:
        if size < size_fin:
            file_fin = file
            size_fin = size
    return file_fin, size_fin

def ChooseFile(filepairs):
    keys = list(filepairs.keys())
    file_fin, size_fin = ChooseMinSize(filepairs[keys[0]])
    for params in keys[1:]:
        file, size = ChooseMinSize(filepairs[params])
        if size > size_fin:
            file_fin = file
            size_fin = size
    return file_fin, size_fin

files = open(paths_in_txt).read().split('\n')
report = {}

for file in files:
    if os.path.exists(file):
        f,n,e = split3(file)
        id_search = re.search(rsp_id_tmpt, n)
        if id_search:
            id = id_search.group()
            if id in report:
                id_files = report[id]
            else:
                id_files = {
                    'SOUR': [],
                    'GRN': [],
                    'RGB': [],
                    'QL': [],
                            }
            if re.search(rsp_source_tmpt, n):
                id_files['SOUR'].append(file)
            elif re.search(rsp_grn_tmpt, n):
                id_files['GRN'].append(file)
            elif re.search(rsp_rgb_tmpt, n):
                id_files['RGB'].append(file)
            elif re.search(rsp_ql_tmpt, n):
                id_files['QL'].append(file)
            # else:
                # print('UNKNOWN FILE TYPE: %s' % n)
            report[id] = id_files
        # else:
            # print('CANNOT GET ID: %s' % n)

size_total = 0
file_export = []
for id in report:
    # print(PrintFiles(id, report[id]))
    grn = report[id]['GRN']
    if grn:
        grn_files = SortById(grn, rsp_grn_tmpt)
        for grn_id in grn_files:
            # scroll(grn_files[grn_id], header=grn_id)
            pairs = FindPairsInList(grn_files[grn_id])
            file, size = ChooseFile(pairs)
            size_total += size
            # print(file)
            file_export.append(file)
    else:
        sour = report[id]['SOUR']
        if sour:
            pairs = FindPairsInList(sour)
            file, size = ChooseFile(pairs)
            size_total += size
            # print(file)
            file_export.append(file)
    rgb = report[id]['RGB']
    if rgb:
        rgb_files = SortById(rgb, rsp_rgb_tmpt)
        for grn_id in rgb_files:
            if grn_id is None:
                print('EXCLUDED: %s' % rgb_files[grn_id])
                continue
            # scroll(grn_files[grn_id], header=grn_id)
            pairs = FindPairsInList(rgb_files[grn_id])
            file, size = ChooseFile(pairs)
            size_total += size
            # print(file)
            file_export.append(file)
print(str_size(size_total))

with open(paths_out_txt,'w') as txt:
    for id in report:
        txt.write(PrintFiles(id, report[id]))

for file in file_export:
    if file.lower().startswith('f'):
        continue
    f, n, e = split3(file)
    file_out = fullpath(out_dir, n, e)
    copymove(file, file_out, True)
