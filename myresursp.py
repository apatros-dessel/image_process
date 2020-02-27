# Functions for processing Resurs-P metadata

from tools import *
from geodata import *

# Examples of Resurs-P metadata filenames
# r'RP1_29073_04_GEOTON_20180905_080656_080715.SCN1.PMS.L2.DC.xml'

# Object containing data about Resurs-P image system

# Templates for Resurs-P metadata filenames
templates = (
    r'RP\d_\d+_\d+_GEOTON_\d+_\d+_\d+.SCN1.PMS.L2.DC.xml',
)

# Raster files indices for Resurs-P scenes
resursp_files = [
    'mul',
]

# Tuples with raster file index and band number for Resurs-P raster data bands
resursp_bandpaths = {

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

resursp_names = OrderedDict(
    {
        'description':  r'<rsp_id>.DC',
        'metadata':     r'<rsp_id>.MD',
        'quality':      r'<rsp_id>.QA',
        'new_metadata': r'new_<rsp_id>.MD',
        'datamask':     r'<rsp_id>.GBD',
        'quicklook':    r'<rsp_id>.QL',
    }
)

# Functions for Resurs-P metadata processing

# Gets Resurs-P file names as ordered dictionary
def get_resursp_filename(kan_id, file_id):
    resursp_name = globals()['resursp_names'].get(file_id)
    if resursp_name is not None:
        resursp_name = resursp_name.replace('<rsp_id>', kan_id)
    return resursp_name

# Returns Resurs-P location id
def get_resursp_location(rsp_id):
    idlist = rsp_id.split('_')
    location = ''.join(idlist[1:3] + [idlist[-1].split(r'.')[1][-1]])
    return location

# Returns Resurs-P datamask filename
def get_resursp_datamask(rsp_id, get_json = True):
    datamask_name = get_resursp_filename(rsp_id, 'datamask')
    if get_json:
        filename = fullpath('', datamask_name, 'json')
    else:
        filename = fullpath('', datamask_name, 'shp')
    return filename

# Fill Resurs-P metadata
def metadata(path):

    meta = scene_metadata('RSP')

    meta.container['description'] = xml2tree(path)

    meta.id = get_from_tree(meta.container.get('description'), 'productId')

    folder, file = os.path.split(path)

    meta.sat =          meta.id[:3]
    meta.fullsat =      meta.id[:3]
    meta.files =        ['mul']

    for file_id in ['metadata', 'quality', 'new_metadata']:
        file_name = get_resursp_filename(meta.id, file_id)
        if file_name is not None:
            file_path = fullpath(folder, file_name, 'xml')
            if os.path.exists(file_path):
                meta.container[file_id] = xml2tree(file_path)

    cur_meta = meta.container.get('metadata')

    if cur_meta is None:
        print('Metadata file not found for {}'.format(meta.id))
    else:
        meta.filepaths = {meta.files[0]: get_from_tree(cur_meta, 'rasterFileName')}
        meta.location =  get_resursp_location(meta.id)
        meta.datetime =  get_date_from_string(get_from_tree(cur_meta, 'firstLineTimeUtc'))
        meta.lvl = get_from_tree(cur_meta, 'productType')

    meta.bandpaths = globals()['resursp_bandpaths'].get(meta.files[0], {})

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
    meta.datamask = get_resursp_datamask(meta.id)
    # print(meta.datamask)
    # meta.cloudmask =      # path to vector data

    try:
        meta.quicklook = get_resursp_filename(meta.id, 'quicklook') + r'.jpg'
    except:
        print('Error writing quicklook for {}'.format(meta.id))

    return meta

# Modules for data processing

product_func = {
    # 'Radiance':     Radiance,
    # 'Reflectance':  Reflectance,
}