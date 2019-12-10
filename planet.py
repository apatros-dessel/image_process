# Functions for processing landsat data

from tools import *

# Examples of Planet metadata filenames
# r'2376743_4865309_2019-05-20_0f2a_BGRN_Analytic_metadata.xml'
# r'20190910_081115_0e26_3B_AnalyticMS_metadata.xml'

imsys_data = object() # Object containing data about Planet image system
imsys_data.template = r'\d+_\d+_\S+_Analytic\S*_metadata.xml'

imsys_data.files = [
    'Analytic',
    'Mask',
]

imsys_data.bands = [
    'blue',
    'green',
    'red',
    'nir',
    'mask',
]

imsys_data.bandspaths = OrderedDict(
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
    datetime = dtime.datetime(year, month, day, hour, minute, second)
    return datetime

# Planet metadata class

class metadata(scene_metadata):

    def __init__(self, path, imsys_data):

        self.container['xmltree'] = xml2tree(path)

        self.sat = get_from_tree(self.container.get('xmltree'), 'serialIdentifier')
        self.files = imsys_data.files
        self.filepaths = getplanetfiles(self.xmltree)
        self.bands = imsys_data.bands
        self.bandpaths = imsys_data.bandpaths

        self.write_time_codes(getplanetdatetime(self.xmltree))

        self.datamask = self.get_datamask_path(path)

    # Gets Planet mask path if one exists
    def get_datamask_path(self, path):
        datamask_template = r'.*{}.*{}.*\.json'.format(self.namecodes.get('[datetime]'), self.sat)
        for filename in os.listdir(path):
            search = re.search(datamask_template, filename)
            if search is not None:
                self.datamask = search.group().strip()
        return None
