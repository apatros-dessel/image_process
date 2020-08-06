# Functions for processing Planet metadata

from tools import *
from geodata import *

# Examples of Planet metadata filenames
# r'2376743_4865309_2019-05-20_0f2a_BGRN_Analytic_metadata.xml'
# r'20190910_081115_0e26_3B_AnalyticMS_metadata.xml'
# r'20190829_033516_1035_3B_AnalyticMS_metadata_clip.xml'

# Object containing data about Planet image system

# Templates for planet metadata filenames
templates = (
    r'\d+_\d+_\S+_Analytic\S*_metadata\S*.xml',
)

# Raster files indices for Planet scenes
planet_files = [
    'Analytic',
    'Mask',
]

# Tuples with raster file index and band number for Planet raster data bands
planet_bandpaths = OrderedDict(
    {
            'blue':     ('Analytic',    1),
            'green':    ('Analytic',    2),
            'red':      ('Analytic',    3),
            'nir':      ('Analytic',    4),
            'mask':     ('Mask',        1),
        }
)

# Functions for planet metadata processing

# Gets Planet file names as ordered dictionary
def getplanetfiles(xml_tree):

    file_list = get_from_tree(xml_tree, 'fileName')
    # scroll(file_list)
    file_dict = OrderedDict()

    for file in file_list:
        if 'DN' in file:
            file_dict['mask'] = file_list.pop(file_list.index(file)).replace('/execdir/', '')
            break

    for file in file_list:
        if 'Analytic' or 'MS' in file:
            file_dict['Analytic'] = file_list.pop(file_list.index(file)).replace('/execdir/', '')
            break

    return file_dict

def getplanetfiles_new(meta):

    tree = meta.container.get('xmltree')

    if tree is None:
        return None

    filepaths = OrderedDict()

    if meta.lvl == 'L3B':
        filepaths['mask'] = meta.name('[id]_DN_udm_clip.tif')
        filepaths['Analytic'] = meta.name('[id]_SR_clip.tif')

    else:
        print('Unknown level: {}'.format(meta.lvl))
        return None

    return filepaths

# Gets Planet scene date and time
def getplanetdatetime(xmltree):
    aq_date_time = get_from_tree(xmltree, 'acquisitionDateTime')
    year, month, day = intlist(aq_date_time[:10].split('-'))
    hour, minute, second = intlist(aq_date_time[11:19].split(':'))
    dtime = datetime(year, month, day, hour, minute, second)
    return dtime

# Fill planet metadata
def metadata(path):

    meta = scene_metadata('PLN')

    meta.container['xmltree'] = planet_tree = xml2tree(path)

    meta.sat = get_from_tree(planet_tree, 'serialIdentifier', digit_to_float=False) # !!! - works incorrectly with some satellites with digit_to_float == True
    meta.fullsat = 'PLN{}'.format(meta.sat)
    meta.id = get_from_tree(planet_tree, 'identifier')
    meta.lvl = get_from_tree(planet_tree, 'productType')
    meta.files = globals()['planet_files']

    loc_id = str(get_from_tree(planet_tree, 'tileId', digit_to_float=False))
    # scroll(loc_id)
    # print(loc_id, len(loc_id))
    # if (loc_id is None):
    if (loc_id is None) or (loc_id in ['[]']):
        loc_id = 'S{}'.format(meta.id.split('_')[1])    # Satellite scene number
    else:
        loc_id = 'T{}'.format(loc_id)                   # Planet tile id (for tiled scenes)
    meta.location = loc_id

    meta.datetime = getplanetdatetime(planet_tree)

    meta.namecodes.update(
        {
            '[sat]':        meta.sat,
            '[lvl]':        meta.lvl,
            '[fullsat]':    meta.fullsat,
            '[id]':         meta.id,
            '[location]':   meta.location,
        }
    )

    # meta.write_time_codes(getplanetdatetime(meta.container.get('xmltree')))
    meta.write_time_codes(meta.datetime)

    meta.filepaths = getplanetfiles(meta.container.get('xmltree'))
    meta.base = 'Analytic'

    # if meta.lvl == 'L3B':
        # meta.filepaths = getplanetfiles_new(meta)
    # else:
        # meta.filepaths = getplanetfiles(meta.container.get('xmltree'))
    # self.bands = imsys_data_obj.bands

    meta.bandpaths = globals()['planet_bandpaths']

    id_code_list = meta.namecodes.get('[id]').split('_')
    datamask_template = r'{}.*\.json'.format('_'.join(id_code_list[:3]), meta.sat)
    for filename in folder_paths(get_corner_dir(path, 2), 1, 'json'):
        search = re.search(datamask_template, filename)
        if search is not None:
            meta.datamask = filename
            # print(meta.datamask)
            break

    return meta

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    # print(feat)
    if meta is not None:
        metadata = meta.container.get('xmltree')
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('datetime', get_from_tree(metadata, 'beginPosition'))
        feat.SetField('clouds', float(get_from_tree(metadata, 'cloudCoverPercentage')[0]))
        feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
        feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sat_view', get_from_tree(metadata, 'spaceCraftViewAngle'))
        feat.SetField('sat_azim', get_from_tree(metadata, 'azimuthAngle'))
        feat.SetField('channels', 4)
        feat.SetField('type', 'MS')
        feat.SetField('format', '16U')
        feat.SetField('rows', get_from_tree(metadata, 'numRows'))
        feat.SetField('cols', get_from_tree(metadata, 'numColumns'))
        feat.SetField('epsg_dat', get_from_tree(metadata, 'epsgCode'))
        feat.SetField('u_size', 'meter')
        feat.SetField('x_size', 3.0)
        feat.SetField('y_size', 3.0)
        feat.SetField('level', get_from_tree(metadata, 'productType'))
        feat.SetField('area', None)
    return feat

# Modules for data processing

# Calculate Radiance
def Radiance(bandpath_in, band_id, bandpath_out, meta, dt = None, compress = None, overwrite = True):

    band_num_id = globals()['planet_bandpaths'][band_id][1] - 1
    mult = reflectanceCoefficient = float(get_from_tree(meta.container.get('xmltree'), 'radiometricScaleFactor')[band_num_id])
    res = MultiplyRasterBand(bandpath_in, bandpath_out, mult, dt=dt, compress=compress, overwrite=overwrite)

    return res

# Calculate Reflectance
def Reflectance(bandpath_in, band_id, bandpath_out, meta, dt = None, compress = None, overwrite = True):

    band_num_id = globals()['planet_bandpaths'][band_id][1] - 1
    mult = reflectanceCoefficient = float(get_from_tree(meta.container.get('xmltree'), 'reflectanceCoefficient')[band_num_id])
    res = MultiplyRasterBand(bandpath_in, bandpath_out, mult, dt=dt, compress=compress, overwrite=overwrite)

    return res

product_func = {
    'Radiance':     Radiance,
    'Reflectance':  Reflectance,
}