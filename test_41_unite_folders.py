from geodata import *

path = r'e:\rks\source\kanopus\2020-06-19'
path_pms = r'd:\terratech\s3\krym_new'
path_out = fullpath(path, 'Krym_fullcover_new.json')

files = []
for p in folder_paths(path, 1, 'shp'):
    if '.MS' in p:
        files.append(p)

# Parse Kanopus name
def parse_kanopus(id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = id.split('_')
    num2, scn, type, lvl = ending.split('.')
    return satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl

def get_neuroid(id):
    if id.startswith('KV'):
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)
        loc = loc1+loc2+scn[4:]
        if type=='PMS':
            lvl += type
    else:
        print('Unknown imsys for: %s' % id)
        return None
    neuroid = '%s-%s-%s-%s' % (satid, date, loc, lvl)
    return neuroid

def kanopus_cover_new(files, pms_path = None):
    feats = VectorFeatureData(files)
    json_fields(path_out,
                ogr.wkbMultiPolygon,
                epsg=4326,
                fields_dict=globals()['fields_dict'],
                feats_list=None,
                field_name_translator=None,
                overwrite=True)

    dout, lout = get_lyr_by_path(path_out, 1)

    lout.DeleteFeature(0)

    if pms_path is not None:
        pms_list = folder_paths(pms_path, 1, 'tif')

    for source_feat in feats:

        feat = feature(feature_defn=lout.GetLayerDefn(), geom=source_feat.GetGeometryRef())

        f, n, e = split3(feats.vec_list[feats.vec_num])
        id = re.search(r'KV[\d,I]_.+\.MS', f).group().replace('.MS', '.PMS.L2')
        satid, loc1, loc2, sentnum, date, num1, num2, scn, type, lvl = parse_kanopus(id)

        meta = open(folder_paths(f,1,'xml')[0]).read()
        date = re.search('dSessionDate = \d\d/\d\d/\d\d\d\d', meta).group()[15:].replace('/','-')
        time = re.search('tSessionTime = \d\d:\d\d:\d\d.\d+', meta).group()[15:]
        sun_elev, sun_azim = flist(re.search('bSunAngle = \d+.\d+, \d+.\d+', meta).group()[12:].split(', '), float)

        feat.SetField('id', id)
        feat.SetField('id_s', '%s%s%s' % (loc1, loc2, scn[3:]))
        feat.SetField('id_neuro', get_neuroid(id))
        feat.SetField('datetime','%sT%s' % (date, time))
        feat.SetField('sun_elev', sun_elev)
        feat.SetField('sun_azim', sun_azim)
        feat.SetField('sat_id', satid)
        feat.SetField('type', 'PMS')
        feat.SetField('format', '16U')
        feat.SetField('u_size', 'meter')
        feat.SetField('level', lvl)

        for pms in pms_list:
            if split3(pms)[1] == id:
                pms_ds = gdal.Open(pms)
                trans = pms_ds.GetGeoTransform()
                epsg = int('326' + re.search(r'"WGS 84 / UTM zone \d+N"', pms_ds.GetProjection()).group()[19:-2])
                feat.SetField('channels', pms_ds.RasterCount)
                feat.SetField('cols', pms_ds.RasterXSize)
                feat.SetField('rows', pms_ds.RasterYSize)
                feat.SetField('channels', pms_ds.RasterCount)
                feat.SetField('x_size', trans[1])
                feat.SetField('x_size', -trans[5])
                feat.SetField('epsg_dat', epsg)
                break

        lout.CreateFeature(feat)

    dout = None

kanopus_cover_new(files, pms_path = path_pms)