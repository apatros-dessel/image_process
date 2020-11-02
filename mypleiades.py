# Functions for processing Pleiades metadata

from tools import *

# Examples of Pleiades metadata filenames
# r'DIM_PHR1B_PMS_201907300445203_ORT_5282598101.XML'

# Object containing data about Pleiades image system

# Templates for Pleiades metadata filenames
templates = (
    r'DIM_PHR\d\w_\w+_\d+_\w+_\d+.XML',
)

# Raster files indices for Pleiades scenes
pleiades_files = [
    'data', # The first file must have the basic resolution for the scene
]

# Tuples with raster file index and band number for Pleiades raster data bands
pleiades_bandpaths = OrderedDict(
    {
            'blue':     ('<raster1_id>',    1),
            'green':    ('<raster1_id>',    2),
            'red':      ('<raster1_id>',    3),
            'nir':      ('<raster1_id>',    4),
        }
)

# STRIP_DS_PHR1A_202008170615476_FR1_PX_E094N68_0321_01654_DIM.XML

# Functions for Pleiades metadata processing

# Gets Pleiades file names and filepaths as list and ordered dictionary respectively
def get_filepaths(tree):
    export = OrderedDict()
    i = 1
    for filepath in get_from_tree(tree, 'DATA_FILE_PATH', attrib='href', sing_to_sing=False):
        file = filepath.lower()
        if file.endswith('.tif'):
            export['data%i' % i] = filepath
            i += 1
        # elif file.endswith('.jpg'):
            # export['image'] = file
    # scroll(export)
    return export

# Gets Pleiades bandpaths as ordered dictionary
def get_bandpaths(filepaths):
    export = OrderedDict()
    for key in filepaths:
            export.update({
                'blue%s' % key[4:]: (key, 3),
                'green%s' % key[4:]: (key, 2),
                'red%s' % key[4:]: (key, 1),
                'nir%s' % key[4:]: (key, 4),
            })
    return export

# Fill Pleiades metadata
def metadata(path):

    meta = scene_metadata('PLD')

    meta.container['meta'] = tree = xml2tree(path)
    id = get_from_tree(tree, 'DATASET_NAME')
    split_ = id.split('_')

    meta.sat =          'PLD' + split_[1][-2:]
    meta.fullsat =      meta.sat
    meta.id =           id
    meta.filepaths =    get_filepaths(tree)
    meta.files =        meta.filepaths.keys()
    meta.lvl =          delist(get_from_tree(tree, 'PROCESSING_LEVEL'))
    meta.bandpaths =    get_bandpaths(meta.filepaths)
    meta.location =     str(int(get_from_tree(tree, 'JOB_ID')))
    meta.datetime =     isodatetime(get_from_tree(tree, 'PRODUCTION_DATE'))

    meta.namecodes.update(
        {
            '[sat]':        meta.sat,
            '[fullsat]':    meta.fullsat,
            '[id]':         meta.id,
            '[location]':   meta.location,
            '[lvl]':        meta.lvl,
        }
    )

    meta.write_time_codes(meta.datetime)

    # Optional:
    for path in get_from_tree(tree, 'COMPONENT_PATH', attrib='href'):
        if re.search(r'/ROI', path):
            meta.datamask =        path
            break
    # meta.cloudmask =      # path to vector data

    return meta

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    # print(feat)
    if meta is not None:
        metadata = meta.container.get('meta')
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('datetime', get_from_tree(metadata, 'PRODUCTION_DATE'))
        feat.SetField('clouds', float(get_from_tree(metadata, 'CLOUD_COVERAGE')))
        feat.SetField('sun_elev', float(get_from_tree(metadata, 'SUN_ELEVATION')[1]))
        feat.SetField('sun_azim', float(get_from_tree(metadata, 'SUN_AZIMUTH')[1]))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sat_view', float(get_from_tree(metadata, 'VIEWING_ANGLE')[1]))
        feat.SetField('sat_azim', float(get_from_tree(metadata, 'AZIMUTH_ANGLE')[1]))
        type = get_from_tree(metadata, 'SPECTRAL_PROCESSING')
        feat.SetField('type', type)
        if type=='PAN':
            feat.SetField('channels', 1)
        else:
            feat.SetField('channels', 4)
        feat.SetField('format', '16U')
        feat.SetField('rows', delist(get_from_tree(metadata, 'NROWS')))
        feat.SetField('cols', delist(get_from_tree(metadata, 'NCOLS')))
        epsg = get_from_tree(metadata, 'PROJECTED_CRS_NAME')
        if epsg==[]:
            epsg = '4326'
        feat.SetField('epsg_dat', epsg)
        feat.SetField('u_size', 'meter')
        x_size = get_from_tree(metadata, 'XDIM')
        if x_size:
            feat.SetField('x_size', delist(x_size))
        y_size = get_from_tree(metadata, 'YDIM')
        if y_size:
            feat.SetField('y_size', delist(y_size))
        feat.SetField('level', meta.lvl)
        feat.SetField('area', float(get_from_tree(metadata, 'SURFACE_AREA'))*1000000)
    return feat