# Functions for processing RapidEye metadata

from tools import *

# Examples of RapidEye metadata filenames
# r'3864411_2019-04-16_RE5_3A_Analytic_metadata_clip.xml'

# Object containing data about RapidEye image system

# Templates for RapidEye metadata filenames
templates = (
    r'\\\d+_.+_RE\d_.+_Analytic_metadata_clip.xml$',
)

# Raster files indices for RapidEye scenes
rapideye_files = [
    'analytic', # The first file must have the basic resolution for the scene
    'udm',
]

# Tuples with raster file index and band number for <imsys_name> raster data bands
rapideye_bandpaths = OrderedDict(
    {
            'blue':     ('analytic',    1),
            'green':    ('analytic',    2),
            'red':      ('analytic',    3),
            'red_edge': ('analytic',    4),
            'nir':      ('analytic',    5),
            'mask':     ('udm',         1),
        }
)

# Functions for RapidEye metadata processing

# Gets <imsys_name> file names as ordered dictionary
def rapydeye_filepaths(tree):
    result = OrderedDict()
    result['analytic'] = get_from_tree(tree, 'fileName')[0].split(r'/')[-1]
    result['udm'] = result['analytic'].replace('Analytic', 'udm')
    return result

# Fill RapidEye metadata
def metadata(path):

    meta = scene_metadata('RYE')

    meta.container['meta'] = tree = xml2tree(path)

    id = split3(path)[1]
    split_ = id.split('_')

    meta.sat =          get_from_tree(tree, 'serialIdentifier')
    meta.fullsat =      split_[2]
    meta.id =           id
    meta.files =        globals()['rapideye_files']
    meta.filepaths =    rapydeye_filepaths(tree)

    meta.bandpaths =    globals()['rapideye_bandpaths']
    meta.location =     split_[0]
    meta.datetime =     isodatetime(get_from_tree(tree, 'acquisitionDateTime'))
    meta.lvl = get_from_tree(tree, 'productType')

    # scroll(meta.datetime)

    meta.namecodes.update(
        {
            '[sat]': meta.sat,
            '[fullsat]': meta.fullsat,
            '[id]': meta.id,
            '[location]': meta.location,
            '[lvl]': meta.lvl,
        }
    )

    meta.write_time_codes(meta.datetime)

    # Optional:
    linkdate = get_from_tree(tree, 'acquisitionDate')[0]
    date, time = re.search('\d+-\d+-\d+T\d+:\d+:\d{2}', linkdate).group().split('T')
    meta.datamask =        meta.name('%s_%s_[location]_[sat]_metadata.json' % (date.replace('-',''), time.replace(':','')))
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
        feat.SetField('datetime', get_from_tree(metadata, 'acquisitionDateTime'))
        feat.SetField('clouds', float(get_from_tree(metadata, 'cloudCoverPercentage')[0]))
        feat.SetField('sun_elev', float(get_from_tree(metadata, 'illuminationElevationAngle')))
        feat.SetField('sun_azim', float(get_from_tree(metadata, 'illuminationAzimuthAngle')))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sat_view', float(get_from_tree(metadata, 'spaceCraftViewAngle')))
        feat.SetField('sat_azim', float(get_from_tree(metadata, 'azimuthAngle')))
        feat.SetField('type', 'MS')
        feat.SetField('channels', 5)
        feat.SetField('format', '16U')
        feat.SetField('rows', int(get_from_tree(metadata, 'numRows')))
        feat.SetField('cols', int(get_from_tree(metadata, 'numColumns')))
        feat.SetField('epsg_dat', int(get_from_tree(metadata, 'epsgCode')))
        feat.SetField('u_size', 'meter')
        feat.SetField('x_size', float(get_from_tree(metadata, 'columnGsd')))
        feat.SetField('y_size', float(get_from_tree(metadata, 'rowGsd')))
        feat.SetField('level', get_from_tree(metadata, 'productType'))
        feat.SetField('area', 0.0)
    return feat