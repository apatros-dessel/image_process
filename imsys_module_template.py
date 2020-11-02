# Functions for processing <imsys_name> metadata

from tools import *

# Examples of <imsys_name> metadata filenames
# r'2376743_4865309_2019-05-20_0f2a_BGRN_Analytic_metadata.xml'
# r'20190910_081115_0e26_3B_AnalyticMS_metadata.xml'

# Object containing data about <imsys_name> image system

# Templates for <imsys_name> metadata filenames
templates = (
    r'<filename_template.ext>',
)

# Raster files indices for <imsys_name> scenes
<imsys_name>_files = [
    '<raster1_id>', # The first file must have the basic resolution for the scene
    'raster2_id',
    '<etc.>',
]

# Tuples with raster file index and band number for <imsys_name> raster data bands
<imsys_name>_bandpaths = OrderedDict(
    {
            'blue':     ('<raster1_id>',    1),
            'green':    ('<raster1_id>',    2),
            'red':      ('<raster1_id>',    3),
            'nir':      ('<raster1_id>',    4),
            'mask':     ('<raster2_id>',    1),
        }
)

# Functions for <imsys_name> metadata processing

# Gets <imsys_name> file names as ordered dictionary
def function1():
    # some code
    return data

# Fill <imsys_name> metadata
def metadata(path):

    meta = scene_metadata('<imsys_id>')

    meta.container['<data_id>'] = # some code to get all metadata

    meta.sat =          # get satellite id as str
    meta.fullsat =      # get satellite fullid as str
    meta.id =           # get scene id as str
    meta.files =        # get files_id list
    meta.filepaths =    # get filepaths as OrderedDict

    meta.bandpaths =    # get bandpaths as tuple of files_id and band numbers
    meta.location =     # get scene location id
    meta.datetime =     # get image datetime as datetime.datetime

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
    # meta.datamsk =        # path to vector data
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
        feat.SetField('datetime', get_from_tree(metadata, 'EARLIESTACQTIME'))
        feat.SetField('clouds', float(get_from_tree(metadata, 'CLOUDCOVER'))*100)
        feat.SetField('sun_elev', get_from_tree(metadata, 'MEANSUNEL'))
        feat.SetField('sun_azim', get_from_tree(metadata, 'MEANSUNAZ'))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sat_view', get_from_tree(metadata, 'MEANOFFNADIRVIEWANGLE'))
        feat.SetField('sat_azim', None)
        if meta.sat == 'WV01':
            feat.SetField('type', 'PAN')
            feat.SetField('channels', 1)
        else:
            feat.SetField('type', 'MS')
            feat.SetField('channels', 4)
        feat.SetField('format', '16U')
        feat.SetField('rows', get_from_tree(metadata, 'NUMROWS'))
        feat.SetField('cols', get_from_tree(metadata, 'NUMCOLUMNS'))
        feat.SetField('epsg_dat', '326%i' % get_from_tree(metadata, 'MAPZONE'))
        feat.SetField('u_size', 'meter')
        feat.SetField('x_size', get_from_tree(metadata, 'COLSPACING'))
        feat.SetField('y_size', get_from_tree(metadata, 'ROWSPACING'))
        feat.SetField('level', get_from_tree(metadata, 'PRODUCTLEVEL'))
        feat.SetField('area', 0.0)
    return feat