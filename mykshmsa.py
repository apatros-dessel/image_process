# Functions for processing <imsys_name> metadata

from tools import *

# Examples of <imsys_name> metadata filenames
# r'RP1_15446_03_KSHMSA-VR_20160329_075052_075122.MS.RS.MD.xml'
# r'RP1_16206_02_KSHMSA-SR_20160517_231336_231522.MS.RS.MD.xml'

# Object containing data about <imsys_name> image system

# Templates for <imsys_name> metadata filenames
templates = (
    r'RP\d_\d+_\d+_KSHMSA-[VS]R_\d+_\d+_\d+.+.RS.MD.xml',
)

# Raster files indices for <imsys_name> scenes
kshmsa_files = [
    'data', # The first file must have the basic resolution for the scene
]

# Tuples with raster file index and band number for <imsys_name> raster data bands
kshmsa_bandpaths = OrderedDict(
    {
            'blue':     ('data',    1),
            'green':    ('data',    2),
            'red':      ('data',    3),
            'nir_':      ('data',    4),
            'nir':     ('data',    5),
        }
)

# Functions for <imsys_name> metadata processing

# Returns KSHMSA data type
def get_kshmsa_type(id):
    if r'.PMS.' in id:
        return 'PMS'
    elif r'.MS.' in id:
        return 'MS'
    elif r'.PAN.' in id:
        return 'PAN'
    else:
        return None

# Fill <imsys_name> metadata
def metadata(path):

    meta = scene_metadata('KSH')

    meta.container = {}
    meta.container['meta'] = cur_meta = xml2tree(path)
    meta.container['dc'] = xml2tree(path.replace('.MD', '.DC'))
    meta.container['qa'] = xml2tree(path.replace('.MD', '.QA'))

    id = Name(path).rstrip('.MD')
    sat = id.split('_')[0]
    meta.sat =          sat
    meta.fullsat =      sat
    meta.id =           id
    meta.files =        ['data']
    meta.filepaths =    {'data': folder_paths(os.path.split(path)[0],1,'tif')[0]}

    meta.bandpaths =    globals()['kshmsa_bandpaths']
    meta.location =     ''.join(id.split('_')[1:3])
    meta.datetime =     get_date_from_string(get_from_tree(cur_meta, 'beginPosition')[0])

    meta.namecodes.update(
        {
            '[sat]':        meta.sat,
            '[fullsat]':    meta.fullsat,
            '[id]':         meta.id,
            '[location]':   meta.location,
        }
    )

    meta.write_time_codes(meta.datetime)

    # Optional:
    meta.datamask = r'%s.GBD.json' % meta.id
    # meta.cloudmask =      # path to vector data
    meta.quicklook = r'%s.QL.jpg' % meta.id
    meta.type = get_kshmsa_type(id)

    return meta

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    # print(feat)
    if meta is not None:
        metadata = meta.container.get('meta')
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('datetime', get_from_tree(metadata, 'beginPosition')[0])
        feat.SetField('clouds', None)
        feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
        feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sat_view', get_from_tree(metadata, 'satelliteViewAngle'))
        feat.SetField('sat_azim', get_from_tree(metadata, 'azimuthAngle'))
        feat.SetField('type', 'MS')
        feat.SetField('format', '16U')
        feat.SetField('rows', get_from_tree(metadata, 'rowCount')[0])
        feat.SetField('cols', get_from_tree(metadata, 'columnCount')[0])
        feat.SetField('epsg_dat', 4326)
        feat.SetField('u_size', 'degree')
        feat.SetField('x_size', None)
        feat.SetField('y_size', None)
        feat.SetField('level', get_from_tree(metadata, 'productType'))
        feat.SetField('area', 0.0)
    return feat