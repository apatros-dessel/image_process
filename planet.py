# Functions for processing Planet metadata

from tools import *

# Examples of Planet metadata filenames
# r'2376743_4865309_2019-05-20_0f2a_BGRN_Analytic_metadata.xml'
# r'20190910_081115_0e26_3B_AnalyticMS_metadata.xml'

# Object containing data about Planet image system

# Templates for planet metadata filenames
templates = (
    r'\d+_\d+_\S+_Analytic\S*_metadata.xml',
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
    file_dict = OrderedDict()

    for file in file_list:
        if 'DN' in file:
            file_dict['mask'] = file_list.pop(file_list.index(file))
            break

    for file in file_list:
        if 'Analytic' or 'MS' in file:
            file_dict['Analytic'] = file_list.pop(file_list.index(file))
            break

    return file_dict

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

    meta.container['xmltree'] = xml2tree(path)

    meta.sat = get_from_tree(meta.container.get('xmltree'), 'serialIdentifier', digit_to_float=False) # !!! - works incorrectly with some satellites with digit_to_float == True
    meta.id = get_from_tree(meta.container.get('xmltree'), 'identifier')
    meta.lvl = get_from_tree(meta.container.get('xmltree'), 'productType')
    meta.files = globals()['planet_files']
    meta.filepaths = getplanetfiles(meta.container.get('xmltree'))
    # self.bands = imsys_data_obj.bands

    meta.bandpaths = globals()['planet_bandpaths']
    meta.datetime = getplanetdatetime(meta.container.get('xmltree'))

    meta.namecodes.update(
        {
            '[sat]':    meta.sat,
            '[id]':     meta.id,
            '[lvl]':    str(meta.lvl),
        }
    )

    # meta.write_time_codes(getplanetdatetime(meta.container.get('xmltree')))
    meta.write_time_codes(meta.datetime)

    datamask_template = r'.*{}.*{}.*\.json'.format(meta.namecodes.get('[datetime]'), meta.sat)
    for filename in os.listdir(os.path.split(path)[0]):
        search = re.search(datamask_template, filename)
        if search is not None:
            meta.datamask = search.group().strip()
            break

    return meta
