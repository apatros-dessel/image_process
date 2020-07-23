# Functions for processing SkySat metadata

from tools import *
from geodata import *

# Examples of SkySat metadata filenames
# r'20200707_112906_ssc7d2_0012_metadata.json'

# Object containing data about SkySat image system

# Templates for SkySat metadata filenames
templates = (
    r'\d{8}_\d+_ss.+_metadata.json',
)

# Raster files indices for SkySat scenes
skysat_files = [
    'Analytic',
    'Mask',
]

# Tuples with raster file index and band number for SkySat raster data bands
skysat_bandpaths = OrderedDict(
    {
        'blue': ('Analytic', 3),
        'green': ('Analytic', 2),
        'red': ('Analytic', 1),
        'nir': ('Analytic', 4),
        'mask': ('Mask', 1),
    }
)

# Functions for SkySat metadata processing

# Gets SkySat file names as ordered dictionary
def get_skysat_files(folder):
    files = OrderedDict()
    img_folder = fullpath(folder, 'analytic')
    if os.path.exists(img_folder):
        for img in os.listdir(img_folder):
            if re.search(r'\d{8}_\d+_.+_analytic.tif', img):
                files['Analytic'] = r'analytic\\%s' % img
            elif re.search(r'\d{8}_\d+_.+_analytic_udm.tif', img):
                files['Mask'] = r'analytic\\%s' % img
    return files

# Fill SkySat metadata
def metadata(path):

    meta = scene_metadata('SS')

    f,n = os.path.split(path)

    DS = ogr.Open(path)
    meta.container['feat'] = feat = DS.GetLayer().GetNextFeature()

    meta.sat =          feat.GetField('satellite_id')
    meta.fullsat =      meta.sat
    meta.id =           feat.GetField('id')
    meta.lvl = feat.GetField('publishing_stage')[:3].upper()

    date, loc1, satcam, loc2 = meta.id.split('_')

    meta.files =        globals()['skysat_files']
    meta.filepaths =    get_skysat_files(f)
    meta.bandpaths =    meta.bandpaths = globals()['skysat_bandpaths']
    meta.location =     loc1 + satcam[-2:] + loc2
    meta.datetime =     get_date_from_string(feat.GetField('acquired'))

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
    meta.datamask =        n
    # meta.cloudmask =      # path to vector data

    return meta

# Adds attributes to a standart feature for cover
def set_cover_meta(feat, meta):
    print(feat)
    if meta is not None:
        feat0 = meta.container.get('feat')
        feat.SetField('id', meta.id)
        feat.SetField('id_s', meta.name('[location]'))
        feat.SetField('id_neuro', meta.name('[fullsat]-[date]-[location]-[lvl]'))
        feat.SetField('datetime', feat0.GetField('acquired'))
        feat.SetField('clouds', float(feat0.GetField('cloud_cover'))*100)
        feat.SetField('sun_elev', float(feat0.GetField('sun_elevation')))
        feat.SetField('sun_azim', float(feat0.GetField('sun_azimuth')))
        feat.SetField('sat_id', meta.name('[fullsat]'))
        feat.SetField('sat_view', float(feat0.GetField('view_angle')))
        feat.SetField('sat_azim', float(feat0.GetField('satellite_azimuth')))
        feat.SetField('channels', 4)
        feat.SetField('type', 'MS')
        feat.SetField('format', '16U')
        # feat.SetField('rows', get_from_tree(metadata, 'numRows'))
        # feat.SetField('cols', get_from_tree(metadata, 'numColumns'))
        # feat.SetField('epsg_dat', get_from_tree(metadata, 'epsgCode'))
        feat.SetField('u_size', 'meter')
        # feat.SetField('x_size', 3.0)
        # feat.SetField('y_size', 3.0)
        feat.SetField('level', meta.lvl)
        feat.SetField('area', 0.0)
    return feat

def meta_from_raster(feat, path):
    raster = gdal.Open(path)
    feat.SetField('rows', raster.RasterYSize)
    feat.SetField('cols', raster.RasterXSize)
    geotrans = raster.GetGeoTransform()
    feat.SetField('x_size', geotrans[1])
    feat.SetField('y_size', -geotrans[5])
    projection = get_srs(raster).ExportToProj4()
    feat.SetField('epsg_dat', int('326' + from_txt(projection, r'\+zone=\d+')[6:]))
    return feat