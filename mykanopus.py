# Functions for processing <imsys_name> metadata

from tools import *
from geodata import *

# Examples of <imsys_name> metadata filenames
# r'KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2'
# r'new_KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2.MD.xml'

# r'KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.MS.L2.DC.xml'
# r'KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.PAN.L2.DC.xml'
# r'KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.PMS.L2.DC.xml'
# r'KVI_13437_09482_00_KANOPUS_20191216_083055_083108.SCN5.MS.L2.DC.xml'

# Object containing data about <imsys_name> image system

# Templates for <imsys_name> metadata filenames
templates = (
    r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PMS.L\d.DC.xml',   # For pan-multispectral data
    r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PAN.L\d.DC.xml',   # For panchromatic data
    r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.MS.L\d.DC.xml',    # For multispectral data
)

# Raster files indices for <imsys_name> scenes
kanopus_files = [
    'mul',
    'pan',
]

# Tuples with raster file index and band number for <imsys_name> raster data bands
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

'''
# Returns Kanopus bandpaths
def get_kanopus_bandpaths(kan_id_list):

    bandpaths = OrderedDict()

    for key in globals()['kanopus_bandpaths']:
        if key in kan_id_list:
            for bandkey in globals()['kanopus_bandpaths'][key]:
                meta.bandpaths[bandkey] = globals()['kanopus_bandpaths'][key][bandkey]

    return bandpaths
'''

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

    meta = scene_metadata('KAN')

    meta.container['description'] = xml2tree(path)

    meta.id = get_from_tree(meta.container.get('description'), 'productId')

    folder, file = os.path.split(path)

    for file_id in ['metadata', 'quality', 'new_metadata']:
        file_name = get_kanopus_filename(meta.id, file_id)
        if file_name is not None:
            file_path = fullpath(folder, file_name, 'xml')
            if os.path.exists(file_path):
                try:
                    meta.container[file_id] = xml2tree(file_path)
                except:
                    pass

    # meta.sat =          get_from_tree(meta.container.get('description'), 'satellite')
    meta.sat =          meta.id[:3]
    meta.fullsat =      meta.id[:3]

    meta.files =        get_kanopus_files(meta.id)

    cur_meta = meta.container.get('metadata')

    if cur_meta is None:
        print('Metadata file not found for {}'.format(meta.id))
    else:
        meta.filepaths = {meta.files[0]: get_from_tree(cur_meta, 'rasterFileName')}
        meta.location = get_kanopus_location(meta.id)
        meta.datetime = get_date_from_string(get_from_tree(cur_meta, 'firstLineTimeUtc'))
        meta.lvl = get_from_tree(cur_meta, 'productType')

    # if meta.container.get('new_metadata') is not None:
        # new_lvl = get_from_tree(cur_meta, 'RASP_ROOT', attrib='cProcLevel')
        # if new_lvl not in (None, []):
            # meta.lvl = new_lvl

    ''' # Kode to get filepath from new_metadata
    meta.filepaths = OrderedDict({meta.files[0]: get_from_tree(cur_meta, 'DataFileName')})
    '''

    # meta.filepaths =    OrderedDict({meta.files[0]:get_from_tree(cur_meta)})

    meta.bandpaths =    globals()['kanopus_bandpaths'].get(meta.files[0], {})

    # for key in globals()['kanopus_bandpaths']:
        # if key in meta.files:
            # for bandkey in globals()['kanopus_bandpaths'][key]:
                # meta.bandpaths[bandkey] = globals()['kanopus_bandpaths'][key][bandkey]

    # datetime.datetime

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

    # Optional:
    meta.datamask = get_kanopus_datamask(meta.id)
    # print(meta.datamask)
    # meta.cloudmask =      # path to vector data

    try:
        meta.quicklook =    get_kanopus_filename(meta.id, 'quicklook') + r'.jpg'
    except:
        print('Error writing quicklook for {}'.format(meta.id))

    return meta

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
