# Functions for processing <imsys_name> metadata

from tools import *

# Examples of <imsys_name> metadata filenames
# r'M20_21081_21081_KMSS100-1_20180801_085158_085342.L2.MD.xml'
# r'M20_01771_01777_MSU-MR_20141110_082547_083358.L2.MD.xml'

# Object containing data about <imsys_name> image system

# Templates for <imsys_name> metadata filenames
templates = (
    r'M20_\d{5}_\d{5}_KMSS100-\d_\d{8}_\d{6}_\d{6}.L2.MD.xml',
    r'M20_\d{5}_\d{5}_KMSS50_\d{8}_\d{6}_\d{6}.L2.MD.xml',
    r'M20_\d{5}_\d{5}_MSU-MR_\d{8}_\d{6}_\d{6}.L2.MD.xml',
)

# Raster files indices for <imsys_name> scenes
meteor_files = [
    'msu-mr', # The first file must have the basic resolution for the scene
    'msu50',
    'msu100',
]

# Tuples with raster file index and band number for <imsys_name> raster data bands
meteor_bandpaths = OrderedDict(
    {
            'red100':     ('msu100',   1),
            'nir100':     ('msu100',   2),
            'green100':   ('msu100',   3),
            'blue50':     ('msu50',    1),
            'green50':    ('msu50',    2),
            'yellow50':   ('msu50',    3),
            'red-mr':     ('msu-mr',   1),
            'nir-mr':     ('msu-mr',   2),
            'swir-mr':    ('msu-mr',   3),
            'mwir-mr':    ('msu-mr',   4),
            'lwir1-mr':   ('msu-mr',   5),
            'lwir2-mr':   ('msu-mr',   6),
        }
)

# Functions for <imsys_name> metadata processing

# Gets Meteor file names as ordered dictionary
def GetFiles(id):
    if 'MSU100' in id:
        return 'msu100'
    elif 'MSU50' in id:
        return 'msu50'
    elif 'MSU-MR' in id:
        return 'msu-mr'

# Gets Meteor file names as ordered dictionary
def GetBandpaths(file):
    report = {}
    bandpaths = globals()['meteor_bandpaths']
    for key in bandpaths:
        keyfile, bandnum = bandpaths[key]
        if keyfile==file:
            report[key] = (keyfile, bandnum)
    return report

# Fill <imsys_name> metadata
def metadata(path):

    meta = scene_metadata('MET')

    meta.container['meta'] = meta = xml2tree(path)
    meta.container['dc'] = xml2tree(path.replace('.MD','.DC'))
    meta.container['qa'] = xml2tree(path.replace('.MD', '.QA'))

    meta.sat =          'M20'
    meta.fullsat =      'M20'
    meta.id =           split3(path)[1].rstrip('.MD')
    meta.files =        GetFiles(meta.id)
    meta.filepaths =    {meta.files[0]: path.replace('MD.xml','tif')}

    meta.bandpaths =    GetBandpaths(meta.files[0])
    meta.location =     ''.join(meta.id.split('_')[1:3])
    meta.datetime =     get_date_from_string(get_from_tree(meta, 'acquisitionDate'))

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
    # meta.datamask =        # path to vector data
    # meta.cloudmask =      # path to vector data
    meta.quicklook =        r'%s.QL.jpg' % meta.id

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