# Functions for processing <imsys_name> metadata

from tools import *
from geodata import *

# Examples of Sentinel-2 metadata filenames
# r'MTD_MSIL1C.xml'

# Object containing data about <imsys_name> image system

# Templates for Sentinel-2 metadata filenames
templates = (
    r'MTD_MSIL\S+.xml',
)

# Raster files indices for <imsys_name> scenes
sentinel_files = [
    'coastal_aerosol', # The first file must have the basic resolution for the scene
    'blue',
    'green',
    'red',
    'vegetation_red_edge_1',
    'vegetation_red_edge_2',
    'vegetation_red_edge_3',
    'nir',
    'narrow_nir',
    'water_vapour',
    'swir-cirrus',
    'swir1',
    'swir2',
    'tci',
    'scene_classification',
    'aot',
    'aot_20m',
    'blue_20m',
    'green_20m',
    'red_20m',
    'tci_20m',
    'coastal_aerosol_60m',
    'blue_60m',
    'green_60m',
    'red_60m',
    'vegetation_red_edge_1_60m',
    'vegetation_red_edge_2_60m',
    'vegetation_red_edge_3_60m',
    'water_vapour_20m',
    'swir1_60m',
    'swir2_60m',
    'tci_60m',
]

sentinel_files_id = [
    ('coastal_aerosol', ('B01')),
    ('blue', ('B02', 'B02_10m')),
    ('green', ('B03', 'B03_10m')),
    ('red', ('B04', 'B04_10m')),
    ('vegetation_red_edge_1', ('B05', 'B05_20m')),
    ('vegetation_red_edge_2', ('B06', 'B06_20m')),
    ('vegetation_red_edge_3', ('B07', 'B07_20m')),
    ('nir', ('B08', 'B08_10m')),
    ('narrow_nir', ('B8A', 'B8A_20m')),
    ('water_vapour', ('B09', 'WVP_10m')),
    ('swir-cirrus', ('B10', 'B10_60m')),
    ('swir1', ('B11', 'B11_20m')),
    ('swir2', ('B12', 'B12_20m')),
    ('tci', ('TCI', 'B10_10m')),
    ('aot', ('AOT_10m')),
    ('scene_classification', ('SCL_20m')),
    ('aot_20m', ('AOT_20m')),
    ('blue_20m', ('B02_20m')),
    ('green_20m', ('B03_20m')),
    ('red_20m', ('B04_10m')),
    ('tci_20m', ('TCI_20m')),
    ('water_vapour_20m', ('WVP_20m')),
    ('aot_60m', ('B10_60m')),
    ('blue_60m', ('B02_60m')),
    ('green_60m', ('B03_10m')),
    ('red_60m', ('B04_60m')),
    ('vegetation_red_edge_1_60m', ('B05_60m')),
    ('vegetation_red_edge_2_60m', ('B06_60m')),
    ('vegetation_red_edge_3_60m', ('B07_60m')),
    ('water_vapour_60m', ('WVP_60m')),
    ('swir1_60m', ('B11_60m')),
    ('swir2_60m', ('B12_60m')),
    ('tci_60m', ('TCI_60m')),
    ('scene_classification_60m', ('SCL_60m')),
]

# Tuples with raster file index and band number for <imsys_name> raster data bands
sentinel_bandpaths = OrderedDict(
    {
        'coastal_aerosol': ('coastal_aerosol', 1),
        'blue': ('blue', 1),
        'green': ('green', 1),
        'red': ('red', 1),
        'vegetation_red_edge_1': ('vegetation_red_edge_1', 1),
        'vegetation_red_edge_2': ('vegetation_red_edge_2', 1),
        'vegetation_red_edge_3': ('vegetation_red_edge_3', 1),
        'nir': ('nir', 1),
        'narrow_nir': ('narrow_nir', 1),
        'water_vapour': ('water_vapour', 1),
        'swir-cirrus': ('swir-cirrus', 1),
        'swir1': ('swir1', 1),
        'swir2': ('swir2', 1),
        'tci_red': ('tci', 1),
        'tci_green': ('tci', 2),
        'tci_blue': ('tci', 3),
        'scene_classification': ('scene_classification', 1),
        'coastal_aerosol_20m': ('coastal_aerosol_20m', 1),
        'blue_20m': ('blue_20m', 1),
        'green_20m': ('green_20m', 1),
        'red_20m': ('red_20m', 1),
        'tci_20m_red': ('tci', 1),
        'tci_20m_green': ('tci', 2),
        'tci_20m_blue': ('tci', 3),
        'coastal_aerosol_60m': ('coastal_aerosol_60m', 1),
        'blue_60m': ('blue_60m', 1),
        'green_60m': ('green_60m', 1),
        'red_60m': ('red_60m', 1),
        'vegetation_red_edge_1_60m': ('vegetation_red_edge_1_60m', 1),
        'vegetation_red_edge_2_60m': ('vegetation_red_edge_2_60m', 1),
        'vegetation_red_edge_3_60m': ('vegetation_red_edge_3_60m', 1),
        'water_vapour_20m': ('water_vapour_20m', 1),
        'swir1_60m': ('swir1_60m', 1),
        'swir2_60m': ('swir2_60m', 1),
        'tci_60m_red': ('tci', 1),
        'tci_60m_green': ('tci', 2),
        'tci_60m_blue': ('tci', 3),
        }
)

# Functions for <imsys_name> metadata processing

# Gets path to Sentinel-2 MSL file
def get_msl_path(path):
    msl_path = path + r'\GRANULE\\'
    msl_path += os.listdir(msl_path)[0]
    msl_path += r'\MTD_TL.xml'
    return msl_path

# Gets <imsys_name> file names as ordered dictionary
def get_sentinel_filepaths(filepath_list):

    sentinel_files_id = globals()['sentinel_files_id']
    sentinel_bandpaths = globals()['sentinel_bandpaths']
    files = []
    filepaths = OrderedDict()
    bandpaths = OrderedDict()

    for fileid, ends_tuple in sentinel_files_id:

        fileid_found = False

        for end in ends_tuple:

            for i, filepath in enumerate(filepath_list):

                if filepath[:-4].endswith(end):

                    files.append(fileid)
                    filepaths[fileid] = filepath_list.pop(i)

                    for bandid in sentinel_bandpaths:

                        band_fileid = sentinel_bandpaths.get(bandid)[0]

                        if band_fileid == fileid:
                            bandpaths[bandid] = sentinel_bandpaths.get(bandid)

                    fileid_found = True
                    break

            if fileid_found:
                break

    if len(filepath_list) > 0:
        scroll(filepath_list, header = 'Some raster files were not processed:')
    # scroll(filepaths)
    # scroll(bandpaths)
    return files, filepaths, bandpaths

# Fill <imsys_name> metadata
def metadata(path):

    meta = scene_metadata('SNT')

    folder = os.path.split(path)[0]

    meta.container['mtd'] = mtd = xml2tree(path)
    meta.container['msl'] = msl = xml2tree(get_msl_path(folder))
    meta.container['manifest'] = manifest = xml2tree(r'{}\manifest.safe'.format(folder))

    meta.sat =          get_from_tree(mtd, 'SPACECRAFT_NAME')
    meta.fullsat =      'S2%{}'.format(meta.sat[-1])
    meta.id =           get_from_tree(mtd, 'PRODUCT_URI')
    meta.lvl =          get_from_tree(mtd, 'PROCESSING_LEVEL').split('-')[1]

    if meta.lvl == '1C':
        filepaths_list = get_from_tree(mtd, 'IMAGE_FILE')
    else:
        filepaths_list = get_from_tree(manifest, 'fileLocation', attrib='href')
        for i in range(len(filepaths_list)-1, -1, -1):
            if 'IMG_DATA' in filepaths_list[i]:
                filepaths_list[i] = filepaths_list[i][1:]
            else:
                filepaths_list.pop(i)

    filepaths_list = get_from_tree(manifest, 'fileLocation', attrib='href')
    for i in range(len(filepaths_list) - 1, -1, -1):
        if 'IMG_DATA' in filepaths_list[i]:
            filepaths_list[i] = filepaths_list[i][1:]
        else:
            filepaths_list.pop(i)

    files, filepaths, bandpaths = get_sentinel_filepaths(filepaths_list)

    meta.files =        files
    meta.filepaths =    filepaths

    meta.bandpaths =    bandpaths
    meta.location =     meta.id.split('_')[5]
    meta.datetime =     get_date_from_string(get_from_tree(mtd, 'PRODUCT_START_TIME'))

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

    # path2mask = r'{}\{}_datamask.shp'.format(tdir().create(), meta.id)
    path2mask = '{}_datamask.shp'.format(meta.id)
    fullpath2mask = fullpath(folder, path2mask)
    # print(path2mask)
    path2mask_data = fullpath(folder, get_from_tree(msl, 'MASK_FILENAME', check = {'type': 'MSK_DETFOO', 'bandId': '2'}))

    JoinShapesByAttributes([path2mask_data], fullpath2mask, attributes = ['maskType'], geom_rule = 1, attr_rule = 0)

    meta.datamask =       path2mask
    meta.cloudmask =      get_from_tree(msl, 'MASK_FILENAME', check = {'type': 'MSK_CLOUDS'})

    return meta

# Modules for data processing

# Calculate Radiance
def Radiance(bandpath_in, band_id, bandpath_out, meta, dt = None, compress = None, overwrite = True):

    band_num_id = globals()['planet_bandpaths'][band_id][1] - 1
    mult = reflectanceCoefficient = float(get_from_tree(meta.container.get('xmltree'), 'radiometricScaleFactor')[band_num_id])
    res = MultiplyRasterBand(bandpath_in, bandpath_out, mult, dt=dt, compress=compress, overwrite=overwrite)

    return res

# Calculate Reflectance
def Reflectance(bandpath_in, band_id, bandpath_out, meta, dt = None, compress = None, overwrite = True):

    if meta.lvl == '1C':
        reflectanceCoefficient = 1/float(get_from_tree(meta.container.get('mtd'), 'QUANTIFICATION_VALUE'))
    elif meta.lvl == '2A':
        reflectanceCoefficient = 1/float(get_from_tree(meta.container.get('mtd'), 'BOA_QUANTIFICATION_VALUE'))

    res = MultiplyRasterBand(bandpath_in, bandpath_out, reflectanceCoefficient, dt=dt, compress=compress, overwrite=overwrite)

    return res

product_func = {
    'Radiance':     Radiance,
    'Reflectance':  Reflectance,
}