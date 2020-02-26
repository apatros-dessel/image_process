# Functions for processing <imsys_name> metadata

from tools import *

# Examples of <imsys_name> metadata filenames
# r'KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2'
# r'new_KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2.MD.xml'

# Object containing data about <imsys_name> image system

# Templates for <imsys_name> metadata filenames
templates = (
    r'KV\d_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d.PMS.L\d.DC.xml',   # For pan-multispectral data
    r'KV\d_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d.PAN.L\d.DC.xml',   # For panchromatic data
    r'KV\d_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d.MS.L\d.DC.xml',    # For multispectral data
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

# Functions for <imsys_name> metadata processing

# Gets <imsys_name> file names as ordered dictionary
def get_kanopus_filename(kan_id, file_id):
    kanopus_name = globals()['kanopus_names'].get(file_id)
    if kanopus_name is not None:
        kanopus_name = kanopus_name.replace('<kan_id>', kan_id)
    return kanopus_name

# Return Kanopus file id list
def get_kanopus_fileid(kan_id):
    if r'.PMS.' in kan_id:
        return ['mul']
    elif r'.MS.' in kan_id:
        return ['mul']
    elif r'.PAN.' in kan_id:
        return ['pan']
    else:
        return None

# Returns Kanopus bandpaths
def get_kanopus_bandpaths(kan_id_list):

    bandpaths = OrderedDict()

    for key in globals()['kanopus_bandpaths']:
        if key in kan_id_list:
            for bandkey in globals()['kanopus_bandpaths'][key]:
                meta.bandpaths[bandkey] = globals()['kanopus_bandpaths'][key][bandkey]

    return bandpaths

# Returns Kanopus datamask filename
def get_kanopus_datamask(kan_id, get_json = False):
    datamask_name = get_kanopus_filename(kan_id, 'datamask')
    if get_json:
        filename = fullpath('', datamask_name, 'json')
    else:
        filename = fullpath('', datamask_name, 'shp')
    return filename

# Returns Kanopus location id
def get_kanopus_location(kan_id):
    idlist = kan_id.split('_')
    try:
        location = ''.join(idlist[1:4] + [idlist[8][-1]])
    except:
        location = ''.join(idlist[1:4] + [idlist[-1].split('.')[1][-1]])
    return location

# Fill <imsys_name> metadata
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
                meta.container[file_id] = xml2tree(file_path)

    meta.sat =          get_from_tree(meta.container.get('description'), 'satellite')
    meta.fullsat =      meta.id[:3]

    meta.files =        get_kanopus_fileid(meta.id)

    cur_meta = meta.container.get('metadata')
    meta.filepaths = OrderedDict({meta.files[0]: get_from_tree(cur_meta, 'rasterFileName')})
    meta.location = get_kanopus_location(meta.id)
    meta.datetime = get_date_from_string(get_from_tree(cur_meta, 'firstLineTimeUtc'))

    meta.lvl = get_from_tree(cur_meta, 'productType')
    if meta.container.get('new_metadata') is not None:
        new_lvl = get_from_tree(cur_meta, 'RASP_ROOT', attrib='cProcLevel')
        if new_lvl not in (None, []):
            meta.lvl = new_lvl

    ''' # Kode to get filepath from new_metadata
    meta.filepaths = OrderedDict({meta.files[0]: get_from_tree(cur_meta, 'DataFileName')})
    '''

    # meta.filepaths =    OrderedDict({meta.files[0]:get_from_tree(cur_meta)})

    meta.bandpaths =    OrderedDict()
    for key in globals()['kanopus_bandpaths']:
        if key in meta.files:
            for bandkey in globals()['kanopus_bandpaths'][key]:
                meta.bandpaths[bandkey] = globals()['kanopus_bandpaths'][key][bandkey]

    print(cur_meta)

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
    print(meta.datamask)
    # meta.cloudmask =      # path to vector data

    return meta