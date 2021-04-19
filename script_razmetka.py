# -*- coding: utf-8 -*-
# Anything was grist that came to the Royal Navy’s mill!

from geodata import *
from image_processor import process
import argparse

parser = argparse.ArgumentParser(description='Razmetka creation options')
parser.add_argument('-v', default=None, dest='vin',  help='Путь к векторному файлу масок (если None или '', то ведётся поиск векторных файлов в директории pin)')
parser.add_argument('-i', default='IM4', dest='imgid', help='Индекс изображений (управляет числом каналов в конечном растре)')
parser.add_argument('-p', default=False, dest='pms', help='Использовать паншарпы')
parser.add_argument('-q', default=None, dest='quicksizes', help='Создать маски квиклуков заданных размеров')
parser.add_argument('-e', default=False, dest='empty', help='Создавать пустые маски при отсутствии вектора')
parser.add_argument('-o', default=True, dest='original', help='Сохранять исходные названия сцен')
parser.add_argument('--image_col', default=None, dest='image_col', help='Название колонки идентификатора растровой сцены (если vin != 0)')
parser.add_argument('--code_col_sec', default=None, dest='code_col_sec', help='Дополнительная колонка с кодовыми значениями')
parser.add_argument('--compress', default='DEFLATE', dest='compress', help='Алгоритм сжатия растровых данных')
parser.add_argument('--overwrite', default=False, dest='overwrite', help='Заменять существующие файлы')
parser.add_argument('--replace', default=None, dest='replace_vals', help='Изменить значения в конечной маске в соответствии со словарём, если None, то замены не производится')
parser.add_argument('--band_reposition', default=None, dest='band_reposition', help='Изменить порядок каналов в конечном растре, если None, то порядок сохраняется')
parser.add_argument('--multiply_band', default=None, dest='multiply_band', help='Перемножить заданные каналы на фиксированный множитель')
parser.add_argument('--dg_metadata', default=None, dest='dg_metadata', help='Путь к хранению метаданных DG')
parser.add_argument('--xls', default=None, dest='input_from_report', help='Путь к таблице xls с путями к источникам данных, если None, то пары снимок-вектор строятся заново. Менять источники можно вручную, формат xlsx не читает')
parser.add_argument('--burn_value', default=None, dest='burn_value', help='Единое значение для всех масок')
parser.add_argument('pin', help='Путь к исходным файлам, растровым или растровым и векторным')
parser.add_argument('pout', help='Путь для сохранения конечных файлов')
parser.add_argument('maskid', help='Тип масок')
parser.add_argument('code_col', help='Название колонки с кодовыми значениями')
args = parser.parse_args()

pin = args.pin
pout = args.pout
maskid = args.maskid
code_col = args.code_col
imgid = args.imgid
vin = args.vin
image_col = args.image_col
original = args.original
code_col_sec = args.code_col_sec
compress = args.compress.upper()
overwrite = boolstr(args.overwrite)
pms = boolstr(args.pms)
quicksizes = liststr(args.quicksizes, tofloat=True)
replace_vals = dictstr(args.replace_vals, toint=True)
band_reposition = liststr(args.band_reposition, toint=True)
multiply_band = dictstr(args.multiply_band, toint=True)
dg_metadata = args.dg_metadata
burn_value = args.burn_value
input_from_report = args.input_from_report
empty_mask = boolstr(args.empty)

if dg_metadata is not None:
    dg_files = folder_paths(dg_metadata,1,'tif')
else:
    dg_files = None

if re.search('^IM[RGBNP]$', imgid) and (band_reposition is None):
    band_reposition = {'R':[1],'G':[2],'B':[3],'N':[4],'P':[1]}[imgid[-1]]

split_vector = False
if vin:
    if os.path.exists(vin) and image_col:
        split_vector = True

vecids_path = None  # Список id при их отсутствии в исходном векторном файле. Если None, то поиск будет производиться в колонке image_col

satellite_types = {
    'Sentinel-2': {'tmpt': r'S2[AB]', 'folder': 'sentinel', 'base_tmpt': '^S2[A,B]', 'band_num': 4},
    'Sentinel-1': {'tmpt': r'S1[AB]', 'folder': 'sentinel-1', 'base_tmpt': '^S1[A,B]', 'band_num': 1},
    'Kanopus': {'tmpt': r'KV[1-6I]', 'folder': 'kanopus', 'base_tmpt': '^KV[1-6I]', 'band_num': 4},
    'Resurs': {'tmpt': r'RP\d', 'folder': 'resurs', 'base_tmpt': '^RP\d', 'band_num': 4},
    'Planet': {'tmpt': r'PLN.+', 'folder': 'planet', 'base_tmpt': 'Analytic', 'band_num': 4},
    'Landsat': {'tmpt': r'LS\d', 'folder': 'landsat', 'base_tmpt': '^LS\d', 'band_num': 4},
    # 'DigitalGlobe': {'tmpt': r'[DW]?[GV]?', 'folder': 'dg', 'base_tmpt': r'[DW]?[GV]?', 'band_num': 4},
}

composite_types = {
    'Sentinel-Sentinel': {'sources': ('Sentinel-2', 'Sentinel-2'), 'folder': 'sentinel-sentinel'},
    'Sentinel-Kanopus': {'sources': ('Sentinel-2', 'Kanopus'), 'folder': 'sentinel-kanopus'},
    'Sentinel-Landsat': {'sources': ('Sentinel-2', 'Landsat'), 'folder': 'sentinel-landsat'},
    'Landsat-Sentinel': {'sources': ('Landsat', 'Sentinel-2'), 'folder': 'landsat-sentinel'},
    'Sentinel-radar': {'sources': ('Sentinel-2', 'Sentinel-1'), 'folder': 'sentinel-radar'},
}

mask_types = {
    u'quarry': {'id': 'MQR', 'folder': 'mines', },
    u'water':    {'id': 'MWT', 'folder': 'water'},
    u'forest':     {'id': 'MFS', 'folder': 'forest'},
    u'change': {'id': 'MCHD', 'folder': 'change'},
    u'full':    {'id': 'MSK', 'folder': 'full'},
    u'svalki':  {'id': 'MWS', 'folder': 'svalki'},
    u'fields_grow': {'id': 'MFG', 'folder': 'fields_grow'},
    u'houses':    {'id': 'MBD', 'folder': 'houses'},
    u'TBO':     {'id': 'MWS', 'folder': 'wastes'},
    u'roads':  {'id': 'MRD', 'folder': 'roads'},
    u'gari':    {'id': 'MFR', 'folder': 'gari'},
    'clouds': {'id': 'MCL', 'folder': 'clouds'},
    'mist': {'id': 'MMI', 'folder': 'mist'},
    'snow': {'id': 'SNW', 'folder': 'snow'},
}

codes = {
    1:  'карьеры (любые)',
    10: 'карьеры, без воды и растительности',
    11: 'карьеры, с растительностью, без воды',
    12: 'карьеры, с водой, без растительности',
    13: 'карьеры, с водой и растительностью',
    2:  'вскрытые грунты (любые)',
    20: 'вскрытые грунты, без воды и растительности',
    21: 'вскрытые грунты, с растительностью, без воды',
    22: 'вскрытые грунты, с водой, без растительности',
    23: 'вскрытые грунты, с водой и ратсительностью',
    24: 'свалки (отдельные маски для свалок с префиксом MDP)',
    25: 'полигоны ТБО',
    26: 'нарушенные земли',
    27: 'гольцы',
    3:  'площадки строительства (любые)',
    30: 'площадки строительства, без воды и растительности',
    31: 'площадки строительства, с растительностью, без воды',
    32: 'площадки строительства, с водой, без растительности',
    33: 'площадки строительства, с водой и растительностью',
    4:  'леса (любые)',
    41: 'лес на болоте',
    411:'широколиственные леса',
    41113:'широколиственные зрелые сомкнутые леса',
    41114:'широколиственные зрелые редкостойные леса',
    41123:'широколиственные молодые сомкнутые леса',
    41124:'широколиственные молодые редкостойные леса',
    412:'мелколиственные леса',
    41213:'мелколиственные зрелые сомкнутые леса',
    41214:'мелколиственные зрелые редкостойные леса',
    41223:'мелколиственные молодые сомкнутые леса',
    41224:'мелколиственные молодые редкостойные леса',
    42: 'светлохвойные леса',
    421:'лиственничники',
    42113:'лиственничники зрелые сомкнутые',
    42114:'лиственничники зрелые редкостойные',
    42123:'лиственничники молодые сомкнутые',
    42124:'лиственничники молодые редкостойные',
    422:'сосняки',
    42213:'сосняки зрелые сомкнутые',
    42214:'сосняки зрелые редкостойные',
    42223:'сосняки молодые сомкнутые',
    42224:'сосняки молодые редкостойные',
    43: 'темнохвойные леса',
    43013:'темнохвойные зрелые сомкнутые леса',
    43014:'темнохвойные зрелые редкостойные леса',
    43023:'темнохвойные молодые сомкнутые леса',
    43024:'темнохвойные молодые редкостойные леса',
    44: 'горельники (без детализации породного состава и интенсивности огня)',
    441:'горельники, пройденные верховым пожаром',
    442:'горельники, пройденные низовым пожаром',
    45: 'зарастание полей',
    5:  'здания (любые)',
    501:'застройка (по среднему и низкому разрешению)',
    51: 'жилые малоэтажные здания',
    52: 'жилые многоэтажные здания',
    53: 'промышленные, коммерческие, исторические и муниципальные здания',
    54: 'автодороги (любые)',
    541:'автодороги с покрытием',
    542:'автодороги грунтовые',
    55: 'железные дороги',
    6:  'болота',
    7:  'изменения (не используется, т.к. аналогичен 100)',
    71: 'снег',
    711:'сплошной снег',
    712:'непостоянный снег',
    72: 'лёд',
    721:'сплошной лёд',
    722:'непостоянный лёд',
    8:  'травянистая растительность (луга, поля и т.д.)',
    81: 'поля',
    811:'поля распаханные, занятые посевами и травяная залежь',
    812: 'поля заброшенные с зарастанием кустарниковой и древесной растительностью',
    9:  'водные объекты (любые)',
    100:'изменения (любые)',
    101:'новые карьеры (любые)',
    102:'новые вскрытые грунты (любые)',
    103:'новые площадки строительства (любые)',
    140:'вырубка (любая)',
    141:'вырубка сплошная',
    142:'вырубка выборочная',
    143:'больной, высохший или сгоревший лес',
    144:'поражение леса верховым пожаром',
    145:'поражение леса низовым пожаром',
    105:'новое строительство зданий и сооружений (любых)',
    151:'новые земляные работы',
    152:'новое дорожное, линейное строительство',
    106:'новые свалки (любые)',
    107:'новое осушение (любое)',
    109:'новое затопление (любое)',
    200:'участки, непригодные для дешифрирования (любые)',
    201:'облака',
    202:'тень облаков',
    203:'дымка',
    2031:'прозрачная дымка',
    2032:'плотная дымка',
    2033:'радужная дымка (несведение каналов)',
    209:'тень от холмов, деревьев, зданий и прочего',
}

while not maskid in mask_types.keys():
    scroll(mask_types.keys(), header='Неизвестный тип разметки - "%s", используйте один из списка:' % maskid)
    try:
        maskid = input('  >>>  ')
    except:
        continue

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Resurs name
def parse_resurs(id):
    # RP1_28244_05_GEOTON_20180713_050017_050036.SCN3.MS.L2
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

# Parse Sentinel-1 name
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
    return satid, date, time, orbit, lvl

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

# Parse DG name
def parse_dg(id):
    print(id)
    satid = 'DG'
    lvl = 'LVL'
    vals = id.split('_')
    months = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
    if re.search(r'.+-S2AS-.+_\d+_P\d+', id):
        datetime, sulvl, loc1 = vals[0].split('-')
        loc = ''.join([loc1,vals[1],vals[2]])
    elif re.search(r'.+-S2AS_R\d+C\d+.*-.+_\d+_P\d+', id):
        datetime = vals[0].split('-')[0]
        newlocs = vals[1].split('-')
        loc4 = ''.join(newlocs[:-1])
        loc1 = newlocs[-1]
        loc = ''.join([loc1,vals[2],vals[3],loc4])
    date = '20%s%s%s' % (datetime[:2], months[datetime[2:5]], datetime[5:7])
    time = datetime[7:]
    return satid, date, time, loc, lvl

def GetMetaDG(id):
    files = globals()['dg_files']
    if files:
        names = flist(files, lambda x: split3(x)[1])
        if id in names:
            file = files[names.index(id)]
            dg_proc = process().input(os.path.dirname(file))
            # scroll(dg_proc.get_ids(), header=id)
            dg_scene = dg_proc.scenes[0]
            satid = dg_scene.meta.name('[sat]')
            date = dg_scene.meta.name('[date]')
            time = dg_scene.meta.name('[time]')
            loc = dg_scene.meta.name('[location]')
            lvl = dg_scene.meta.name('[lvl]')
            # print(satid, date, time, loc, lvl)
            return satid, date, time, loc, lvl
    else:
        return parse_dg(id)

# Расширенная функция расчёта neuroid, учитывающая готовые neuroid и названия разновременных композитов
def neuroid_extended(id, original=False):
    cutsearch = re.search('__cut\d+$', id)
    if cutsearch is not None:
        cut = cutsearch.group()
        id = id[:-len(cut)]
    else:
        # print('NoCut: %s' % id)
        cut = ''
    if re.search(r'^IM\d+-.+-\d+-.+-.+$', id):
        return id + cut
    elif re.search(r'^S[12][AB]-\d+-.+-.+$', id):
        return 'IM4-' + id + cut
    elif re.search(r'IMCH\d+__.+__.+', id):
        parts = id.split('__')[1:3]
    elif len(id.split('__'))==2:
        parts = id.split('__')
    else:
        newid = get_neuroid(id, original=original)
        if newid is not None:
            return newid + cut
        else:
            print('WRONG ID: %s' % id)
            return None
    vals = [globals()['imgid']]
    # scroll(parts)
    for part_id in parts:
        part_neuroid = neuroid_extended(part_id, original=original)
        vals.append(part_neuroid[part_neuroid.index('-')+1:])
    return '__'.join(vals) + cut

# Получить neuroid из исходного имени файла (для 4-х канального RGBN)
def get_neuroid(id, original=False):
    if original:
        return id
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
    elif re.search(r'^RP.+L2', id):
        id = re.search(r'^RP.+L2', id).group()
        satid, loc1, sentnum, date, num1, num2, scn, type, lvl, grn = parse_resurs(id)
        loc = loc1 + scn[3:]
        if type == 'PMS':
            lvl += type
    elif re.search(r'^S2[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel(id)
    elif re.search(r'^S1[AB]', id) or re.search(r'^S2.+cut\d+$', id):
        satid, date, time, loc, lvl = parse_sentinel1(id)
    elif re.search(r'^LC08_', id):
        satid, date, loc, lvl = parse_landsat8(id)
    elif re.search(r'.+-S2AS.+_P\d+', id):
        dg_id = re.search(r'^.+P\d+', id).group()
        dg_metavals = GetMetaDG(dg_id)
        if dg_metavals is None:
            return None
        else:
            satid, date, time, loc, lvl = dg_metavals
    else:
        print('Unknown imsys for: %s' % id)
        return None
    imgid = globals()['imgid']
    neuroid = imgid+'-%s-%s-%s-%s' % (satid, date, loc, lvl)
    # IM4 в начале -- условность, его можно будет изменить на этапе обработки изображения, если в нём больше 4 каналов
    return neuroid

# Получить список значений колонки векторного файла
def get_col_keys(vec, colname):
    din, lin = get_lyr_by_path(vec)
    if lin is None:
        return None
    else:
        keys = []
        for feat in lin:
            key = feat.GetField(colname)
            if (key is not None) and (key not in keys):
                keys.append(key)
        return keys

# Обработать искажённые индексы растровых файлов с тем, чтобы получить правильное название растра
# Работает только в случае, когда нужно извлекать хитро выебанные названия файлов из атрибутов вектора
# Для временных композитов не сработает, проще заставить поставщика предоставить по одному векторному файлу на каждый растр
def filter_id(id, pms=False):
    for tmpt in (r'KV.+SCN\d+', r'IM\d+-.+-L2', r'IM\d+-.+\d{2,}', r'^S2.+\d+T\d+$', r'RP.+L2.GRN\d+'):
        search = re.search(tmpt, id)
        if search:
            report = search.group()
            # Для случая, когда вектор уже создан по переименованному растру
            # Найти растр с оригинальным именем по neuroid не выйдет -- предполагается, что если соответствующий растр есть у поставщика данных, то у нас будет и подавно
            if report.startswith('IM4'):
                if not report.endswith('-L2'):
                    report += '-L2'
                if pms:
                    report += 'PMS'
            # Редкая ошибка для переформатированных имён Канопусов
            elif report.startswith('KV'):
                report = report.replace('_SCN', '.SCN')
                if pms:
                    report += '.PMS.L2'
                else:
                    report += '.MS.L2'
                # report = get_neuroid(report)
            return report

def check_nonzeros(path):
    l = len(np.unique(gdal.Open(path),GetRasterBand(1).ReadAsArray()))
    return bool(l)

def get_raster_paths(raster_path):
    raster_path = obj2list(raster_path)
    pinstr = '\n'.join(pin)
    if os.path.exists(globals()['source_paths']):
        with open(globals()['source_paths']) as path_data:
            pin_, paths_ = path_data.read().split('\n\n')
            if pin_ == pinstr:
                return paths_.split('\n')
    export = []
    for folder in raster_path:
        export.extend(folder_paths(folder, 1, 'tif'))
    with open(globals()['source_paths'], 'w') as path_data:
        path_data.write('{}\n\n{}'.format(pinstr, '\n'.join(export)))
        print('Written source paths to: %s' % globals()['source_paths'])
    return export

# Checks if name must be excluded as pansharpened or not pansharpened
def pms_exit(id, pms = False):
    if re.search('KV.+SCN\d+.+', id):
        if id.endswith('PMS'):
            if not pms:
                return True
        else:
            if pms:
                return True
    return False

# Получить пути к исходным данным для масок для разделённых векторных файлов (shp, json, geojson) и растровых снимков (tif)
def get_pair_paths(pin, pms = False, original = False):
    export = OrderedDict()
    for folder in obj2list(pin):
        paths = folder_paths(folder, 1)
        for path in paths:
            f,n,e = split3(path)
            if not e in ['shp', 'json', 'geojson', 'tif']:
                continue
            id = neuroid_extended(n, original=original)
            if id is None:
                if e=='tif':
                    print(path)
                continue
            if pms_exit(id, pms):
                continue
            if e == 'tif':
                if id in export:
                    export[id]['r'] = path
                else:
                    export[id] = {'r': path}
            elif e in ('shp', 'json', 'geojson'):
                if id in export:
                    export[id]['v'] = path
                else:
                    export[id] = {'v': path}
    for id in export:
        if ('v' in export[id]) and ('r' in export[id]):
            export[id]['pairing'] = True
        else:
            export[id]['pairing'] = False
    return export

# Получить пути к исходным данным для масок для цельных векторных файлов
def get_pairs(raster_paths, vin, img_colname, vecids=None, split_vector=True, pms=False, original=False):
    export = OrderedDict()
    if vecids is None:
        vecids = get_col_keys(vin, img_colname)
    raster_names = flist(raster_paths, lambda x: split3(x)[1])
    for vecid in vecids:
        id = filter_id(vecid, pms=pms)
        for i, rasterid in enumerate(raster_names):
            if id == rasterid:
                try:
                    neuroid = neuroid_extended(n, original=original)
                    if split_vector:
                        export[neuroid] = {'r': raster_paths[i], 'v': filter_dataset_by_col(vin, img_colname, vecid)}
                    else:
                        export[neuroid] = {'r': raster_paths[i], 'v': vin}
                    export[neuroid]['pairing'] = True
                except:
                    if not ('neuroid' in locals()):
                        neuroid = vecid
                    if neuroid:
                        if neuroid in export:
                            export[neuroid]['pairing'] = False
                        else:
                            export[neuroid] = {'pairing': False}
                finally:
                    print('%s pairing %s' % (('ERROR', 'SUCCESS')[bool(neuroid)], vecid))
                    break
    return export

# Получить полные пути к растрам в разметке (автоматически создаётся нужная директория)
def get_paths(pout, id, maskid, imgid, quicksizes):
    satellite_types = globals()['satellite_types']
    fail = True
    if re.search(r'IMCH\d+__.+__.+', id) and re.search('^IMCH\d+$', imgid):
        composite_types = globals()['composite_types']
        nameparts = id.split('__')
        # scroll(nameparts)
        name1, name2 = nameparts[1:3]
        for compid in composite_types:
            sat1 = satellite_types[composite_types[compid]['sources'][0]]['tmpt']
            sat2 = satellite_types[composite_types[compid]['sources'][1]]['tmpt']
            if re.search(sat1, name1.split('-')[0]) and re.search(sat2, name2.split('-')[0]):
                sat_folder = composite_types[compid]['folder']
                nameparts[0] = imgid
                imgname = '__'.join(nameparts)
                fail = False
                break
        if fail:
            print('Unknown time composite for %s')
            return None
    elif re.search(r'^IM[0-9RGBNP]+-.+-\d+-.+-.+$', id) and re.search('^IM[0-9RGBNP]+$', imgid):
        for satid in satellite_types:
            if re.search(satellite_types[satid]['tmpt'], id.split('-')[1]):
                sat_folder = satellite_types[satid]['folder']
                nameparts = id.split('-')
                nameparts[0] = imgid
                imgname = '-'.join(nameparts)
                fail = False
        if fail:
            print('Unknown satellite for: %s' % id)
            return None
    else:
        for satid in satellite_types:
            if re.search(satellite_types[satid]['base_tmpt'], id):
                sat_folder = satellite_types[satid]['folder']
                imgname = id
                fail = False
        if fail:
            print('Wrong id format: %s' % id)
            return None
    img_folder = r'%s\images\%s' % (pout, sat_folder)
    msk_type = globals()['mask_types'].get(maskid)
    if msk_type:
        msk_folder = r'%s\masks\%s\%s' % (pout, msk_type['folder'], sat_folder)
    else:
        print('Unknown mask type: %s' % msk_type)
        return None
    for folder in (img_folder, msk_folder):
        suredir(folder)
    img_path = fullpath(img_folder, imgname, 'tif')
    if imgname.startswith('IM'):
        if len(imgid) == 3:
            msk_name = msk_type['id']+id[3:]
        else:
            msk_name = msk_type['id'] + id[4:]
    else:
        msk_name = id
    msk_path = fullpath(msk_folder, msk_name, 'tif')
    if quicksizes:
        quickpaths = OrderedDict()
        for size in quicksizes:
            strsize = size2str(size)
            ql_img_folder = r'%s\quicklook\%s\images\%s' % (pout, strsize, sat_folder)
            suredir(ql_img_folder)
            ql_img_path = r'%s\%s__QL%s.tif' % (ql_img_folder, imgname, strsize)
            ql_msk_folder = r'%s\quicklook\%s\masks\%s\%s' % (pout, strsize, msk_type['folder'], sat_folder)
            suredir(ql_msk_folder)
            ql_msk_path = r'%s\%s__QL%s.tif' % (ql_msk_folder, msk_name, strsize)
            quickpaths[size] = (ql_img_path, ql_msk_path)
    else:
        quickpaths = None
    return (img_path, msk_path, quickpaths)

# Check if the image needs repair
def check_image(img_in, neuro, multiply = None):
    raster = gdal.Open(img_in)
    realBandNum = raster.RasterCount
    metaBandNum = 0
    img_type = neuro.split('__')[0].split('-')[0]
    if re.search(r'^IM\d+$', img_type):
        metaBandNum = int(img_type[2:])
    elif re.search(r'IM[RGBNP]$', img_type):
        metaBandNum = 1
    elif re.search(r'IMCH\d+$', img_type):
        metaBandNum = int(img_type[4:])
    elif '.PAN' in neuro:
        metaBandNum = 1
    else:
        satellite_types = globals()['satellite_types']
        for satid in satellite_types:
            if re.search(satellite_types[satid]['base_tmpt'], neuro):
                metaBandNum = satellite_types[satid]['band_num']
    counter = min((metaBandNum, realBandNum))
    if multiply is not None:
        return True, counter
    if metaBandNum > realBandNum:
        print('Not enough bands for: %s - got %i, need %i' % (img_in, realBandNum, metaBandNum))
        raise Exception
    elif metaBandNum < realBandNum:
        print('Band count mismatch for: %s - got %i, need %i' % (img_in, realBandNum, metaBandNum))
        return True, counter
    counter = min((metaBandNum, realBandNum))
    for i in range(1, counter + 1):
        band = raster.GetRasterBand(i)
        if band.DataType != 3 or band.GetNoDataValue() != 0:
            return True, counter
    return False, counter

# Записать изображение, проверяя корректность его формата
# Если overwrite==False, то изображения в корректном формате пропускаются
def set_image(img_in, img_out, overwrite = False, band_reposition = None, multiply = None):
    if os.path.exists(img_out):
        repair, counter = check_image(img_out, split3(img_out)[1])
        if not (repair or overwrite):
            return img_out
    if os.path.exists(img_in):
        repair, counter = check_image(img_in, split3(img_out)[1], multiply=multiply)
    else:
        print('Path not found: %s' % img_in)
        return 'ERROR: Source file not found'
    if repair:
        return repair_img(img_in, img_out, counter, band_order = band_reposition, multiply = multiply)
    else:
        shutil.copyfile(img_in, img_out)
        return img_out

# Записать растр снимка в установленном формате
def repair_img(img_in, img_out, count, band_order=None, multiply = None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':3, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(band_order, range(1, count+1)):
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
        if multiply is not None:
            if bin in multiply.keys():
                arr_ = arr_ * multiply[bin]
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out

# Создать растровую маску на основе вектора
def set_mask(img_in, vec_in, msk_out, overwrite=False, empty_value=0, burn_value=None):
    if check_exist(msk_out, ignore=overwrite):
        return msk_out
    if os.path.exists(vec_in):
        crs = get_srs(gdal.Open(img_in))
        vec_reprojected = tempname('shp')
        vec_to_crs(ogr.Open(vec_in), crs, vec_reprojected)
        if not os.path.exists(vec_reprojected):
            vec_reprojected = vec_in
        try:
            if burn_value is None:
                RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, value_colname=code_col, value_colname_sec=code_col_sec, compress=compress, overwrite=overwrite)
            else:
                RasterizeVector(vec_reprojected, img_in, msk_out, data_type=2, burn_value=burn_value, compress=compress, overwrite=overwrite)
            return msk_out
        except:
            # RasterizeVector(vec_reprojected, img_out, msk_out, data_type=2, value_colname=code_col, value_colname_sec=code_col_sec, compress=compress, overwrite=overwrite)
            print('Rasterizing error: %s %s' % (img_in, vec_in))
            return 'ERROR: Rasterizing error'
    else:
        try:
            # ds(msk_out, copypath=img_in, options={'bandnum': 1, 'dt': 1, 'compress': 'DEFLATE'}, overwrite=overwrite)
            CreateDataMask(img_in, msk_out, value=empty_value, nodata=0, bandnum=1)
            return msk_out
        except:
            print('Rasterizing error: %s %s' % (img_in, vec_in))
            return 'ERROR: Rasterizing error'

# Создать загрублённые снимки и растровые маски на основе вектора
def set_quicklook(img_in, vec_in, ql_out, msk_out, pixelsize=None, method=gdal.GRA_Average, empty_value=0, burn_value=None, overwrite=True):
    MakeQuicklook(img_in, ql_out, epsg=None, pixelsize=pixelsize, method=method, overwrite=overwrite)
    set_mask(ql_out, vec_in, msk_out, empty_value=empty_value, burn_value=burn_value, overwrite=overwrite)

def size2str(size):
    strsize = str(size).strip(' 0')
    if strsize.endswith('.'):
        strsize = strsize[:-1]
    return strsize

def QlPathStr(str0, ql_add):
    if str0 is None:
        return None
    else:
        for spliter in [r'\images', '\masks']:
            pathparts = str0.split(spliter)
            if len(pathparts)==2:
                pout, partpath = pathparts
                return '%s\quicklook\%s%s%s__QL%s.tif' % (pout, ql_add, spliter, partpath[:-4], ql_add)

def qlReport(folder, input, size):
    ql_input = OrderedDict()
    strsize = size2str(size)
    codes = globals()['codes']
    msk_end_values = OrderedDict()
    for line in input:
        _dict = input[line]
        new_line = '%s__QL%s' % (line, strsize)
        new_dict = OrderedDict()
        new_dict['r'] = _dict.get('r')
        new_dict['v'] = _dict.get('v')
        new_dict['pairing'] = _dict.get('pairing')
        new_dict['img_out'] = QlPathStr(_dict.get('img_out'), strsize)
        new_dict['msk_out'] = msk_out = QlPathStr(_dict.get('msk_out'), strsize)
        if os.path.exists(str(msk_out)):
            vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))
            for val in vals:
                if val and (not val in msk_end_values):
                    if val in codes:
                        msk_end_values[val] = codes[val]
                    else:
                        print('Unknown code: %i' % val)
                        msk_end_values[val] = 'UNKNOWN'
            msk_values = ' '.join(flist(vals, str))
            new_dict['report'] = 'SUCCESS'
            new_dict['msk_values'] = msk_values
        else:
            new_dict['report'] = 'FAILURE'
            new_dict['msk_values'] = ''
        ql_input[new_line] = new_dict
    dict_to_csv(fullpath(folder, 'mask_values.csv'), msk_end_values)
    report_name = 'report_{}.xls'.format(datetime.now()).replace(' ', '_').replace(':', '-')
    report_path = fullpath(folder, report_name)
    dict_to_xls(report_path, ql_input)

def check_type(codes):
    type_dict = {a: 0 for a in mask_types}
    mines = list(range(1,4)) + list(range(10,14)) + list(range(20,24)) + list(range(26,27)) + list(range(30,34))
    for c in codes:
        if c in mines:
            type_dict[u"quarry"] += 1
        elif c == 9:
            type_dict[u"water"] += 1
        elif str(c)[0] == '4': # 44,45 are for forest fires only
            type_dict[u"forest"] += 1
        elif c in range(100, 200) or c == 7:
            type_dict[u"change"] += 1
        elif c in range(200, 209):
            type_dict["clouds"] += 1
        elif c == 24:
            type_dict[u"svalki"] += 1
        elif str(c)[0] == 8:
            type_dict[u"fields_grow"] += 1
        elif str(c)[0] == '5' and c != 54:
            type_dict[u"houses"] += 1
        elif c == 25:
            type_dict[u"TBO"] += 1
        elif c == 54:
            type_dict[u"roads"] += 1
        elif c == 44 or c == 45:
            type_dict[u"gari"] += 1
    return type_dict

###################################################################################

t = datetime.now()
# Найти пары снимок-вектор для создания масок
if input_from_report:
    input = xls_to_dict(input_from_report)
    print('Input taken from %s' % input_from_report)
else:
    if vin is None or vin == '':
        input = get_pair_paths(pin, pms=pms, original=original)
    else:
        vecids = None
        if vecids_path is not None:
            if os.path.exists(vecids_path):
                with open(vecids_path) as vecids_data:
                    vecis = vecids_data.read().split('\n')
        raster_paths = get_raster_paths(pin)
        input = get_pairs(raster_paths, vin, image_col, vecids=vecids, split_vector=split_vector, pms=pms, original=original)
    print('Input collected for {}'.format(datetime.now()-t))

# Создать пути для размещения изображений и масок
suredir(pout)
# scroll(input, header='\nTotal input:')

# Создавать маски из найденных пар
t = datetime.now()
msk_end_values = {}

try:
    if not (re.search('^IMCH\d+$', imgid) or re.search('^IM[0-9RGBNP]+$', imgid)):
        raise Exception('\n  WRONG imgid: {}, "IM[0-9RGBNP]+" or "IMCH\d+" is needed\n'.format(imgid))
    for i, neuroid in enumerate(input):
        if (neuroid is None):
            print('  %i -- NEUROID ERROR: %s\n' % (i+1, str(neuroid)))
            continue
        elif input[neuroid]['pairing']==False:
            if empty_mask and os.path.exists(str(input[neuroid].get('r'))):
                # print('  %i -- VECTOR NOT FOUND, CREATING EMPTY MASK: %s\n' % (i, str(neuroid)))
                pass
            else:
                print('  %i -- PAIRING ERROR: %s\n' % (i+1, str(neuroid)))
                continue
        paths = get_paths(pout, neuroid, maskid, imgid, quicksizes)
        if paths:
            img_out, msk_out, quickpaths = paths
            img_in = input[neuroid]['r']
            vec_in = input[neuroid].get('v', '')
            if '&full_cloud' in img_in:
                empty_value = 201
            else:
                empty_value = 0
            img_out = set_image(img_in, img_out, overwrite=overwrite, band_reposition=band_reposition, multiply=multiply_band)
            input[neuroid]['img_out'] = img_out
            msk_out = set_mask(img_in, vec_in, msk_out, empty_value=empty_value, burn_value=burn_value, overwrite=overwrite)
            input[neuroid]['msk_out'] = msk_out
            if quickpaths:
                for size in quickpaths:
                    ql_img_out, ql_msk_out = quickpaths[size]
                    set_quicklook(img_out, vec_in, ql_img_out, ql_msk_out, pixelsize=size, method=gdal.GRA_Average,
                                  empty_value=empty_value, overwrite=overwrite)
            if not msk_out.startswith('ERROR'):
                replace = replace_vals
                if replace is not None:
                    try:
                        ReplaceValues(msk_out, replace)
                        input[neuroid]['report'] = 'SUCCESS'
                        if quickpaths:
                            for size in quickpaths:
                                ReplaceValues(quickpaths[size][1], replace)
                    except:
                        print('Error replacing values: %s' % neuroid)
                        input[neuroid]['report'] = 'ERROR: Mask names not replaced'
                else:
                    input[neuroid]['report'] = 'SUCCESS'
                try:
                    vals = list(np.unique(gdal.Open(msk_out).ReadAsArray()))
                    all_codes = check_type(vals)
                    max_type = max(all_codes, key=lambda key: all_codes[key])
                    if max_type != maskid:
                        print("Warning: masktype %s mismatch maskid %s" % (max_type, maskid))
                    for val in vals:
                        if val and (not val in msk_end_values):
                            if val in codes:
                                msk_end_values[val] = codes[val]
                            else:
                                print('Unknown code: %i' % val)
                                msk_end_values[val] = 'UNKNOWN'
                    msk_values = ' '.join(flist(vals, str))
                except:
                    print('Cannot get mask values for: %s' % neuroid)
                    msk_values = ''
                input[neuroid]['msk_values'] = msk_values
                print('  %i -- MASKED: %s with %s\n' % (i+1, neuroid, msk_values))
            else:
                print('  %i -- ERROR: %s\n' % (i + 1, neuroid))
        else:
            input[neuroid]['report'] = 'ERROR: Source paths not found'
            print('  %i -- ERROR: Source paths not found for %s\n' % (i + 1, neuroid))
except:
    print('\n ERROR CREATING MASK \n')
finally:
    report_name = 'report_{}.xls'.format(datetime.now()).replace(' ','_').replace(':','-')
    report_path = fullpath(pout, report_name)
    dict_to_xls(report_path, input)
    scroll(msk_end_values, header='CODES USED:')
    dict_to_csv(fullpath(pout, 'mask_values.csv'), msk_end_values)
    print('FINISHED -- REPORT SAVED TO %s' % report_path)
    if quicksizes:
        for size in quicksizes:
            ql_report = qlReport(r'%s\quicklook\%s' % (pout, size2str(size)), input, size)
print(datetime.now()-t)
