# Functions for processing Kanopus metadata

from tools import *
from geodata import *

# Examples of Kanopus metadata filenames
# r'KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2'
# r'new_KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2.MD.xml'

# r'KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.MS.L2.DC.xml'
# r'KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.PAN.L2.DC.xml'
# r'KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.PMS.L2.DC.xml'
# r'KVI_13437_09482_00_KANOPUS_20191216_083055_083108.SCN5.MS.L2.DC.xml'
# r'fr1_KV1_32147_25610_01_3NP2_07_S_595808_080518.xml'
# r'fr_0041_0102_03146_1_03135_08_00.xml'

# Object containing data about Kanopus image system

# Templates for Kanopus metadata filenames
templates = (
    r'KV.+_KANOPUS_.+SCN\d+.+.MD.xml',
    # r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PMS.L\d.DC.xml',   # For pan-multispectral data
    # r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PAN.L\d.DC.xml',   # For panchromatic data
    # r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.MS.L\d.DC.xml',    # For multispectral data
    # r'fr\d+_KV\d+_.+NP.+\.xml',                                      # For new metadata type
    # r'fr_[0-9_]+\.xml',                                              # For new metadata type 2
    # r'fr_[0-9_]+_ORT_K\.xml',                                        # For new metadata type 2 with orthotransform
)

# Raster files indices for Kanopus scenes
kanopus_files = [
    'mul',
    'pan',
]

# Tuples with raster file index and band number for Kanopus raster data bands
kanopus_bandpaths = {

    'mul':  {

                'green':    ('mul',     2),
                'blue':     ('mul',     3),
                'red':      ('mul',     1),
                'nir':      ('mul',     4),
            },

    'pan':  {
                'pan':      ('pan',     1),
            },
}

# Indices for Kanopus filenames
kanopus_ids = OrderedDict(
    {
        'metadata':     'MD',
        'quality':      'QA',
    }
)

kanopus_names = OrderedDict(
    {
        'description':  r'<kan_id>.DC',
        'metadata':     r'<kan_id>.MD',
        'quality':      r'<kan_id>.QA',
        'new_metadata': r'new_<kan_id>.MD',
        'datamask':     r'<kan_id>.GBD',
        'quicklook':    r'<kan_id>.QL',
    }
)

# Functions for Kanopus metadata processing

# Gets Kanopus file names as ordered dictionary
def get_kanopus_filename(kan_id, file_id):
    kanopus_name = globals()['kanopus_names'].get(file_id)
    if kanopus_name is not None:
        kanopus_name = kanopus_name.replace('<kan_id>', kan_id)
    return kanopus_name

# Return Kanopus file id list
def get_kanopus_files(kan_id):
    if r'.PMS.' in kan_id:
        return ['mul']
    elif r'.MS.' in kan_id:
        return ['mul']
    elif r'.PAN.' in kan_id:
        return ['pan']
    else:
        return None

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

# Parse Kanopus name (alternate)
def parse_kanopus_alternate(id):
    fr, satid, loc1, loc2, sentnum, np, scn, type, num1, num2, ob = id.split('_')
    return satid, loc1, loc2, sentnum, fr, num1, num2, scn

# Returns Kanopus datamask filename
def get_kanopus_datamask(kan_id, get_json = True):
    datamask_name = get_kanopus_filename(kan_id, 'datamask')
    if get_json:
        filename = fullpath('', datamask_name, 'json')
    else:
        filename = fullpath('', datamask_name, 'shp')
    return filename

# Returns Kanopus location id
def get_kanopus_location(kan_id):
    idlist = kan_id.split('_')
    location = ''.join(idlist[1:3] + [idlist[-1].split(r'.')[1][-1]])
    return location

# Returns Kanopys data type
def get_kanopus_type(kan_id):
    if r'.PMS.' in kan_id:
        return 'PMS'
    elif r'.MS.' in kan_id:
        return 'MS'
    elif r'.PAN.' in kan_id:
        return 'PAN'
    else:
        return None

# Fill Kanopus metadata
def metadata(path):
    f,n,e = split3(path)
    if re.search(r'fr\d+_KV\d+_.+NP.+\.xml', path):
    # if False:
        meta =  get_alternate_metadata(path)
        # print(meta.files, meta.filepaths)
    else:
        meta = scene_metadata('KAN')
        # meta.container['description'] = xml2tree(path)
        # meta.id = get_from_tree(meta.container.get('description'), 'productId')
        meta.id = split3(path)[1].replace('.MD','')
        folder, file = os.path.split(path)
        for file_id in ['description', 'metadata', 'quality', 'new_metadata']:
            file_name = get_kanopus_filename(meta.id, file_id)
            if file_name is not None:
                file_path = fullpath(folder, file_name, 'xml')
                if os.path.exists(file_path):
                    try:
                        meta.container[file_id] = xml2tree(file_path)
                    except:
                        pass
        meta.files = get_kanopus_files(meta.id)
        cur_meta = meta.container.get('metadata')
        if cur_meta is None:
            print('Metadata file not found for {}'.format(meta.id))
        else:
            meta.filepaths = {meta.files[0]: get_from_tree(cur_meta, 'rasterFileName')}
            meta.location = get_kanopus_location(meta.id)
            meta.datetime = get_date_from_string(get_from_tree(cur_meta, 'firstLineTimeUtc'))
            meta.lvl = get_from_tree(cur_meta, 'productType')

        datamask = get_kanopus_datamask(meta.id)
        if os.path.exists(fullpath(f,datamask)):
            meta.datamask = datamask
        else:
            paths = folder_paths(f,1,'shp')
            if len(paths)==1:
                meta.datamask = os.path.basename(paths[0])

        try:
            meta.quicklook = get_kanopus_filename(meta.id, 'quicklook') + r'.jpg'
        except:
            print('Error writing quicklook for {}'.format(meta.id))
    # print(meta.files, meta.filepaths)
    meta.sat =          meta.id[:3]
    meta.fullsat =      meta.id[:3]
    meta.bandpaths =    globals()['kanopus_bandpaths'].get(meta.files[0], {})
    meta.namecodes.update(
        {
            '[sat]':        meta.sat,
            '[lvl]':        meta.lvl,
            '[fullsat]':    meta.fullsat,
            '[id]':         meta.id,
            '[location]':   meta.location,
        }
    )
    meta.write_time_codes(meta.datetime)

    return meta

# Gets metadata from alternate format
def get_alternate_metadata(path):
    meta = scene_metadata('KAN')
    meta.container['NP'] = txt = open(path).read()
    # print(txt)
    meta.id = from_txt(txt, r'DataFileName = ".+"')[16:-1]
    satid, loc1, loc2, sentnum, fr, num1, num2, scn_num = parse_kanopus_alternate(meta.id)
    meta.files = [{'PAN':'pan','MS':'mul','PMS':'mul'}.get(get_type_alternate(txt))]
    meta.filepaths = {meta.files[0]: ('%s.tif' % meta.id[:-3].replace('_OB','')).replace('..','.')}
    meta.location = loc1+loc2+scn_num
    date = from_txt(txt, 'SessionDate = \d+/\d+/\d+')[14:]
    time = from_txt(txt, 'SessionTime = \d+:\d+:\d+.\d+')[14:]
    meta.datetime = get_date_from_string('%s-%s-%sT%s' % (date[-4:], date[3:5], date[:2], time))
    meta.lvl = from_txt(txt, 'ProcLevel = ".+"')[13:-1]
    meta.datamask = ('%s.shp' % meta.id[:-3].replace('_OB','')).replace('..','.')
    meta.quicklook = '%s.jpg' % meta.id[:-3]
    return meta

# Get Kanopus type from alternate metadata
def get_type_alternate(txt):
    ch = int(from_txt(txt, 'Samples = \d+')[10:])
    if ch == 1:
        return 'PAN'
    elif '_S_' in txt:
        return 'MS'
    elif '_PSS1_' in txt:
        return 'PMS'

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    if meta is not None:
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('clouds', None)  # The cloud cover percent data are available for only PMS scenes and usually look implausible
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('format', '16U')
        feat.SetField('area', 0.0)
        feat.SetField('u_size', 'meter')
        feat.SetField('level', meta.name('[lvl]'))

        if meta.container.get('metadata'):
            metadata = meta.container.get('metadata')
            feat.SetField('datetime', get_from_tree(metadata, 'firstLineTimeUtc'))
            feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
            feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
            feat.SetField('sat_view', get_from_tree(metadata, 'satelliteViewAngle'))
            feat.SetField('sat_azim', get_from_tree(metadata, 'azimuthAngle'))
            if '.PAN' in meta.id:
                feat.SetField('channels', 1)
                feat.SetField('type', 'PAN')
            elif '.MS' in meta.id:
                feat.SetField('channels', 4)
                feat.SetField('type', 'MS')
            elif '.PMS' in meta.id:
                feat.SetField('channels', 4)
                feat.SetField('type', 'PMS')
            feat.SetField('rows', get_from_tree(metadata, 'rowCount')[1])
            feat.SetField('cols', get_from_tree(metadata, 'columnCount')[1])
            feat.SetField('epsg_dat', int('326' + re.search(r'WGS 84 / UTM zone \d+N', get_from_tree(metadata, 'wktString')).group()[18:-1]))
            feat.SetField('u_size', 'meter')
            feat.SetField('x_size', get_from_tree(metadata, 'productResolution'))
            feat.SetField('y_size', get_from_tree(metadata, 'productResolution'))
        elif meta.container.get('NP'):
            txt = meta.container.get('NP')
            feat.SetField('datetime', meta.name('[year]/[month]/[day]T[hour]:[minute]:[second]'))
            sel, saz = from_txt(txt, 'SunAngle = \d+.\d+, \d+.\d+')[11:].split(', ')
            feat.SetField('sun_elev', float(sel))
            feat.SetField('sun_azim', float(saz))
            feat.SetField('sat_view', None)
            feat.SetField('sat_azim', None)
            ch = int(from_txt(txt, 'Samples = \d+')[10:])
            feat.SetField('channels', ch)
            feat.SetField('type', get_type_alternate(txt))
            feat.SetField('rows', int(from_txt(txt, 'Height = \d+')[9:]))
            feat.SetField('cols', int(from_txt(txt, 'Width = \d+')[8:]))
    return feat

def meta_from_raster(feat, path):
    raster = gdal.Open(path)
    geotrans = raster.GetGeoTransform()
    feat.SetField('x_size', geotrans[1])
    feat.SetField('y_size', -geotrans[5])
    projection = get_srs(raster).ExportToProj4()
    feat.SetField('epsg_dat', int('326' + from_txt(projection, r'\+zone=\d+')[6:]))
    return feat

# Modules for data processing

# Calculate Reflectance
def Reflectance(bandpath_in, band_id, bandpath_out, meta, dt = None, compress = None, overwrite = True):

    kan_type = get_kanopus_type(meta.id)

    if kan_type == 'PAN':
        reflectanceCoefficient = float(get_from_tree(meta.container.get('metadata'), 'radiometricScaleFactor'))

    elif kan_type == 'MS':
        coef_list = get_from_tree(meta.container.get('metadata'), 'radiometricScaleFactor')
        descr_list = get_from_tree(meta.container.get('metadata'), 'bandDescription')
        for descr, coef in zip(descr_list, coef_list):
            if str(bandpath_in[1]) in descr:
                reflectanceCoefficient = coef
                break

    elif kan_type == 'PMS':
        print('Reflectance calculation not supported for Kanopus  PMS data')
        return 1

    else:
        print('Unknown Kanopus data type: %s' % kan_type)
        return 1

    res = MultiplyRasterBand(bandpath_in, bandpath_out, reflectanceCoefficient, dt=dt, compress=compress, overwrite=overwrite)

    return res

product_func = {
    # 'Radiance':     Radiance,
    'Reflectance':  Reflectance,
}
