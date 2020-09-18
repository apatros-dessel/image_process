# Functions for processing Digital Globe metadata

from tools import *

# Examples of Digital Globe metadata filenames
# r'20MAY02084412-S2AS-012719021010_01_P001.XML'

# Object containing data about <imsys_name> image system

# Templates for Digital Globe metadata filenames
templates = (
    r'\d\d\w+\d+-.+-\d+_\d\d_P\d+.XML',
)

# Raster files indices for Digital Globe scenes
dg_files = [
    'data', # Source data 16 bit BGRN EPSG:4326
    'image', # Image 8 bit RGB EPSG:3857
]

# Tuples with raster file index and band number for Digital Globe raster data bands
dg_bandpaths = OrderedDict(
    {
            'blue':     ('data',    1),
            'green':    ('data',    2),
            'red':      ('data',    3),
            'nir':      ('data',    4),
            'red_img':  ('image',   1),
            'green_img':('image',   2),
            'blue_img': ('image',   3),
        }
)

dg_sats = {
    'WV01': 'WorldView-1',
    'WV02': 'WorldView-2',
    'WV03': 'WorldView-3',
    'WV04': 'WorldView-4',
    'GE01': 'GeoEye-1',
}

# Functions for Digital Globe metadata processing

# Gets DG file names as ordered dictionary
def get_filepaths(folder):
    export = OrderedDict()
    files = os.listdir(folder)
    # print(files)
    i = 1
    for file in files:
        file = file.lower()
        if file.endswith('.tif'):
            export['data%i' % i] = file
            i += 1
        elif file.endswith('.jpg'):
            export['image'] = file
    return export

def get_bandpaths(filepaths):
    export = OrderedDict()
    for key in filepaths:
        if key.startswith('data'):
            export.update({
                'blue%s' % key[4:]: (key, 1),
                'green%s' % key[4:]: (key, 2),
                'red%s' % key[4:]: (key, 3),
                'nir%s' % key[4:]: (key, 4),
            })
        elif key=='image':
            export.update({
                'red_img': ('image', 1),
                'green_img': ('image', 2),
                'blue_img': ('image', 3),
            })
    return export

def get_baselist(filepaths):
    baselist = list(filepaths.keys())
    baselist.pop(baselist.index('image'))
    return baselist

# Gets DG scene date and time
def get_dg_datetime(meta):
    date, time = get_from_tree(meta, 'EARLIESTACQTIME').split('T')
    year, month, day = flist(date.split('-'), int)
    hour, minute, second = flist(time[:8].split(':'),int)
    dtime = datetime(year, month, day, hour, minute, second)
    return dtime

# Gets DG datamask vector path
def get_dg_datamask(folder, name):
    base, n = os.path.split(folder)
    gis_folder = fullpath(base, 'GIS_FILES')
    if os.path.exists(gis_folder):
        for vec in folder_paths(gis_folder,1,'shp'):
            if re.search(name, vec):
                return vec

# Fill Digital Globe metadata
def metadata(path):

    meta = scene_metadata('DG')

    meta.container['meta'] = dg = xml2tree(path)

    folder, file, ext = split3(path)

    meta.sat =          delist(get_from_tree(dg, 'SATID', digit_to_float=False))
    meta.fullsat =      meta.sat # globals()['dg_sats'].get(meta.sat)
    meta.lvl =          delist(get_from_tree(dg, 'PRODUCTLEVEL'))
    meta.id =           delist(get_from_tree(dg, 'CATID', digit_to_float=False))
    # meta.files =        globals()['dg_files']
    meta.filepaths =    get_filepaths(folder)
    meta.files =        meta.filepaths.keys()
    meta.bandpaths =    get_bandpaths(meta.filepaths)
    meta.base =         get_baselist(meta.filepaths)
    loc_list = get_from_tree(dg, 'PRODUCTORDERID', digit_to_float=False).split('_')
    meta.location =     ''.join(loc_list[:2])
    meta.datetime =     get_dg_datetime(dg)

    meta.namecodes.update(
        {
            '[sat]':        meta.sat,
            '[fullsat]':    meta.fullsat,
            '[lvl]':        meta.lvl,
            '[id]':         meta.id,
            '[location]':   meta.location,
        }
    )

    meta.write_time_codes(meta.datetime)

    # Optional:
    meta.datamask =        get_dg_datamask(folder, file)
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