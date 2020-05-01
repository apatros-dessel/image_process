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