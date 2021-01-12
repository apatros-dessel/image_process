from tools import *
from geodata import *

path0 = r'\\172.21.195.215\thematic\ЦЗ_диск'

folders, files = folder_paths(path0, filter_folder=['Космические снимки'])

for file in files:
    f,n,e = split3(file)
    dir0, folder_name = os.path.split(f)
    if n.startswith(folder_name):
        new_file = file
    else:
        new_file = fullpath(f,folder_name+'_'+n,e)
        os.rename(file, new_file)
    print(new_file)

sys.exit()
# namepath = r'\\172.21.195.2\FTP-Share\ftp\Change_detection\SAR_Sentinel1\Sentinel_difficult_winter\original_imgs'
            # r'\\172.21.195.2\FTP-Share\ftp\Change_detection\SAR_Sentinel1\Sentinel_difficult_winter\original_imgs'
# namepath = r'\\172.21.195.2\FTP-Share\ftp\Change_detection\SAR_Sentinel1\Siberia\original_imgs'
namepath = r'\\172.21.195.2\FTP-Share\ftp\Change_detection\SAR_Sentinel1\Tverskaya\original_imgs'
sourcepath = r'e:\rks\razmetka_source\sentinel_radar_tver'
imgid = 'IMCH6'

def get_namelist(path):
    return flist(os.listdir(path), lambda x: x.replace('.SAFE',''))

def get_sourcenames(path):
    names_list = []
    for file in folder_paths(path, 1, 'tif'):
        f,n,e = split3(file)
        if not n in names_list:
            names_list.append(n)
    return names_list

def rename(namein, namelist):
    split_ = namein.split('_')
    if len(split_)==5:
        subset, s2tile, s2date, s1, s1date = split_
    elif len(split_)==6:
        subset, s2tile, s2date, s1, s1date, val = split_
    else:
        print('Wrong namein: %s' % namein)
        return None, None
    s2tile = s2tile.replace('s2','')
    s1date = s1date.split('.')[0]
    s2list =[]
    s1list = []
    for name in namelist:
        if name.startswith('S2'):
            # print('S2: %s' % name)
            if (s2tile in name) and (s2date in name):
                s2list.append(name)
        elif name.startswith('S1'):
            # print('S1: %s' % name)
            if s1date in name:
                s1list.append(name)
        else:
            print('Wrong name: %s' % name)
    return s1list, s2list

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Resurs name
def parse_resurs(id):
    satid, loc1, sentnum, geoton, date, num1, ending = id.split('_')
    ending = ending.split('.')
    if len(ending) == 4:
        num2, scn, type, lvl = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, ''
    elif len(ending) == 5:
        num2, scn, type, lvl, grn = ending
        return satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn
    else:
        raise Exception('Wrong ending length for %s' % id)

# Parse Sentinel name
def parse_sentinel(id):
    # S2B_MSIL1C_20190828T043709_N0208_R033_T48VUP_20190828T082130
    # S2A_MSIL1C_20190828_T37VCD # shortid for time composits
    vals = id.split('_')
    if len(vals) == 7:
        satid, lvl, datetime, col, row, tile, datetime2 = id.split('_')
        cutid = ''
    elif len(vals) == 8:
        satid, lvl, datetime, col, row, tile, datetime2, cutid = id.split('_')
        tile += cutid
    elif len(vals) == 6:
        satid, lvl, datetime, col, row, tile = id.split('_')
    elif len(vals) == 4:
        satid, lvl, datetime, tile = id.split('_')
    else:
        return '', '', '', '', ''
    lvl = lvl[-3:]
    dt = datetime.split('T')
    if len(dt)==2:
        date, time = dt
    else:
        date = dt[0]
        time = ''
    return satid, date, time, tile, lvl

# Parse Sentinel name
def parse_sentinel1(id):
    # S1B_IW_GRDH_1SDV_20190108T231417_20190108T231442_014409_01AD29_1DD8.SAFE
    vals = id.split('_')
    if len(vals) == 9:
        satid, mode, typeclass, lvl, datetime1, datetime2, orbit, ad, dd = vals
        lvl = mode+lvl+typeclass
    else:
        return '', '', '', '', ''
    dt = datetime1.upper().split('T')
    if len(dt)==2:
        date, time = dt
    else:
        date = dt[0]
        time = ''
    location = orbit+dd
    return satid, date, time, location, lvl

# Parse Landsat-8 name
def parse_landsat8(id):
    vals = id.split('_')
    # LC08_L1TP_133019_20160830_20170321_01_T1
    if len(vals)==4:
        satid, lvl, date, loc = vals
    elif len(vals)==7:
        satid, lvl, loc, date, date2, lvl1, lvl2 = vals
    else:
        return '', '', '', ''
    if satid=='LC08':
        satid = 'LS8'
    if not (bool(re.search(r'\d{6}', loc)) and bool(re.search(r'\d{8}', date))):
        loc_ = date
        date = loc
        loc = loc_
    return satid, date, loc, lvl

# Расширенная функция расчёта neuroid, учитывающая готовые neuroid и названия разновременных композитов
def neuroid_extended(id):
    cutsearch = re.search('__cut\d+$', id)
    if cutsearch is not None:
        cut = cutsearch.group()
        id = id[:-len(cut)]
    else:
        print('NoCut: %s' % id)
        cut = ''
    if re.search(r'^IM\d+-.+-\d+-.+-.+$', id):
        return id
    elif re.search(r'IMCH\d+__.+__.+', id):
        parts = id.split('__')[1:3]
    elif len(id.split('__'))==2:
        parts = id.split('__')
    else:
        return get_neuroid(id)
    vals = [globals()['imgid']]
    # scroll(parts)
    for part_id in parts:
        part_neuroid = neuroid_extended(part_id)
        vals.append(part_neuroid[part_neuroid.index('-')+1:])
    return '__'.join(vals) + cut

# Получить neuroid из исходного имени файла (для 4-х канального RGBN)
def get_neuroid(id):
    if re.search(r'^KV.+L2$', id):
        id = re.search(r'KV.+L2', id).group()
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[3:]
        if type == 'PMS':
            lvl += type
    # Ресурс-П обрабатывается только из гранул!
    elif re.search(r'^RP.+L2.GRN\d+$', id):
        id = re.search(r'RP.+L2.GRN\d+', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = parse_resurs(id)
        loc = loc1 + scn[3:] + grn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^S2[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel(id)
    elif re.search(r'^S1[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel1(id)
    elif re.search(r'^LC08_', id):
        satid, date, loc, lvl = parse_landsat8(id)
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = imgid+'-%s-%s-%s-%s' % (satid, date, loc, lvl)
    # IM4 в начале -- условность, его можно будет изменить на этапе обработки изображения, если в нём больше 4 каналов
    return neuroid

source_list = get_sourcenames(sourcepath)
names_list = get_namelist(namepath)

scroll(source_list)
#sys.exit()
rename_dict = OrderedDict()
for source in source_list:
    s1, s2 = rename(source, names_list)
    if s1 and s2:
        if len(s1)==1 and len(s2)==1:
            name_fin = 'IMCH6__%s__%s' % ('-'.join(get_neuroid(s2[0]).split('-')[1:]), '-'.join(get_neuroid(s1[0]).split('-')[1:]))
        else:
            # scroll(s1, header='%s Sentinel-1' % source)
            # scroll(s2, header='%s Sentinel-2' % source, lower = ' ')
            test_dict = OrderedDict()
            for s1file in s1:
                cover_file = r'%s\\%s.SAFE\\preview\\map-overlay.kml' % (namepath, s1file)
                ds_in, lyr_in = get_lyr_by_path(cover_file)
                if lyr_in:
                    feat = lyr_in.GetNextFeature()
                    s1geom = feat.GetGeometryRef()
                    rgeom = RasterGeometry(gdal.Open(fullpath(sourcepath, source, 'tif')), lyr_in.GetSpatialRef())
                    rgeom = changeXY(rgeom)
                    test_dict[s1file] = rgeom.Intersection(s1geom).Area()/rgeom.Area()
            name_fin = 'IMCH6__%s__%s' % ('-'.join(get_neuroid(s2[0]).split('-')[1:]), '-'.join(get_neuroid(dict_max_key(test_dict)).split('-')[1:]))
        if len(source.split('_'))==6:
            name_fin = '%s__cut%s' % (name_fin, source.split('_')[-1])
        rename_dict[source] = name_fin
    else:
        rename_dict[source] = None

scroll(rename_dict)
sys.exit()

for file in folder_paths(sourcepath,1):
    folder, name = os.path.split(file)
    for source in rename_dict.keys():
        if rename_dict[source]:
            if source in name:
                os.rename(file, fullpath(folder, name.replace(source, rename_dict[source])))
