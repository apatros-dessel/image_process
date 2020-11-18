# Functions for processing Resurs-P metadata

from tools import *
from geodata import *

# Examples of Resurs-P metadata filenames
# r'RP1_29073_04_GEOTON_20180905_080656_080715.SCN1.PMS.L2.DC.xml'
# r'RP1_36120_04_GEOTON_20191209_080522_080539.SCN2.PAN.L2.DC.xml'
# r'RP1_36120_04_GEOTON_20191209_080522_080539.SCN2.MS.L2.DC.xml'

# Object containing data about Resurs-P image system

# Templates for Resurs-P metadata filenames
templates = (
    r'RP\d_\d+_\d+_GEOTON_\d+_\d+_\d+.SCN\d.PMS.L2.DC.xml',
    r'RP\d_\d+_\d+_GEOTON_\d+_\d+_\d+.SCN\d.MS.L2.DC.xml',
    r'RP\d_\d+_\d+_GEOTON_\d+_\d+_\d+.SCN\d.PAN.L2.DC.xml',
)

# Raster files indices for Resurs-P scenes
resursp_files = [
    'pan',
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

# Return Resurs-P file id list
def get_resursp_files(rsp_id):
    if r'.PMS.' in rsp_id:
        return ['mul']
    elif r'.MS.' in rsp_id:
        return ['mul']
    elif r'.PAN.' in rsp_id:
        return ['pan']
    else:
        return None

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
    meta.files =        get_resursp_files(meta.id)

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
    # meta.cloudmask =      # path to vector data

    try:
        meta.quicklook = get_resursp_filename(meta.id, 'quicklook') + r'.jpg'
    except:
        print('Error writing quicklook for {}'.format(meta.id))

    return meta

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    if meta is not None:
        metadata = meta.container.get('metadata')
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('datetime', get_from_tree(metadata, 'firstLineTimeUtc'))
        feat.SetField('clouds', None) # The cloud cover percent data are available for only PMS scenes and usually look implausible
        feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
        feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
        feat.SetField('sat_id', meta.name('[fullsat]'))
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
        feat.SetField('format', '16U')
        feat.SetField('rows', get_from_tree(metadata, 'rowCount')[1])
        feat.SetField('cols', get_from_tree(metadata, 'columnCount')[1])
        feat.SetField('epsg_dat', int('326' + re.search(r'WGS 84 / UTM zone \d+N', get_from_tree(metadata, 'wktString')).group()[18:-1]))
        feat.SetField('u_size', 'meter')
        feat.SetField('x_size', get_from_tree(metadata, 'productResolution'))
        feat.SetField('y_size', get_from_tree(metadata, 'productResolution'))
        feat.SetField('level', get_from_tree(metadata, 'productType'))
        feat.SetField('area', None)
    return feat

# Modules for data processing

product_func = {
    # 'Radiance':     Radiance,
    # 'Reflectance':  Reflectance,
}