# -*- coding: utf-8 -*-

from geodata import *
from shutil import copyfile

def crop_bigraster_gdal(path_in, path_vec, path_out):
    command = "gdalwarp -of GTiff -cutline {path_vec} -crop_to_cutline -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 {path_in} {path_out}".format(path_vec=path_vec, path_in=path_in, path_out=path_out)
    # print(command)
    os.system(command)

def resurs_granule_index(filename):
    satid, loc1, sentnum, resurs, date, num1, ending = undersplit = filename.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    lvl = dotsplit[3]
    granule = dotsplit[-1]
    scn_num = scn.replace('SCN', '')
    if not granule.startswith('GRN'):
        granule = ('GRN' + granule)
    indexname = '{}-{}-{}{}{}-{}'.format(satid, date, loc1, scn_num, granule, lvl)
    return indexname

def granule_metadata_json(path_granule, path_cover_meta, path_out, raster_path):
    # Get input data
    copyfile(path_cover_meta, path_out)
    dout, lout = get_lyr_by_path(path_out, 1)
    dgr, lgr = get_lyr_by_path(path_granule)
    fout = lout.GetNextFeature()
    fgr = lgr.GetNextFeature()
    # Set new geometry as intersection of tile and scene vector cover
    geom = fout.GetGeometryRef().Intersection(fgr.GetGeometryRef())
    fout.SetGeometry(geom)
    # Set new metadata
    granule_id = str(int(fgr.GetField('granule')))
    tile_id = '%s.GRN%s' % (fout.GetField('id'), granule_id)
    # print(tile_id)
    fout.SetField('id', tile_id)
    fout.SetField('id_neuro', resurs_granule_index(tile_id))
    fout.SetField('id_s', fout.GetField('id_neuro').split('-')[2])
    # Get new metadata from raster
    rgr = gdal.Open(raster_path)
    fout.SetField('rows', rgr.RasterYSize)
    fout.SetField('cols', rgr.RasterXSize)
    # Save new feature
    lout.SetFeature(fout)
    dout = None



path_in = r'\\tt-nas-archive\Dockstation-HDD\102_2020_108_PSH' # Путь к исходным сценам Ресурс-П
raster_fullcover = r'\\tt-nas-archive\Dockstation-HDD\102_2020_108_PSH\Resurs_krym_new_fullcover.json'      # Путь к файлу покрытия Ресурс-П
vector_path = r'\\tt-nas-archive\Dockstation-HDD\granules_grid.shp'                                         # Путь кфайлу сетки гранул
out_dir = r'\\tt-nas-archive\Dockstation-HDD\102_2020_108_PSH_GRN'                                          # Путь к готовым гранулам
filter_path = r'e:\\temp\datatable.xls'       # Путь к файлу фильтра (txt или xls)
compid = 'Serg_work'    # Id данного компьютера (нужно прописывать вручную)

if filter_path.endswith('.txt'):
    try:
        filter_txt = open(filter_path)
        if filter_txt is not None:
            filter = []
            filter_list = filter_txt.split('\n')
            for line in filter_list:
                if re.search(r'^r.*.l2$', line.strip().lower()) is not None:
                    filter.append(line.strip())
    except:
        filter = None
elif filter_path.endswith('.xls'):
    try:
        print(filter_path)
        filter_dict = xls_to_dict(filter_path)
        # scroll(filter_dict, header = 'filter_dict:')
        if filter_dict is not None:
            filter = []
            for id in filter_dict.keys():
                cid = filter_dict[id].get('compid')
                q = filter_dict[id].get('qual')
                s = filter_dict[id].get('status')
                if (cid==compid) and (q=='good') and (s!='done'):
                    filter.append(id)
    except:
        filter = None

suredir(out_dir)

loop = OrderedDict()

# filter = [r'RP1_27955_05_GEOTON_20180624_081010_081022.SCN2.PMS.L2']
scroll(filter, header='Filter:')

# sys.exit()

for fpath in folder_paths(path_in, 1):
    f = os.path.basename(fpath)
    if re.search(r'^r.*.l2\.tif$', f.lower(), flags=0):
        id, ext = os.path.splitext(f)
        print(id)
        if filter is not None:
            if not (id in filter):
                continue
        loop[id] = {'tif': fpath}
        loop[id]['json'] = filter_dataset_by_col(raster_fullcover, 'id', id, path_out=tempname('json'))

scroll(loop)

for i, id in enumerate(loop):

    raster_path = loop[id].get('tif')
    raster_cover_path = loop[id].get('json')

    if None in (raster_path, raster_cover_path):
        continue

    crop_ds, crop_lyr = get_lyr_by_path(vector_path)
    cover_ds, cover_lyr = get_lyr_by_path(raster_cover_path)
    cover_feat = cover_lyr.GetNextFeature()
    cover_geom = cover_feat.GetGeometryRef()

    for feat in crop_lyr:
        granule_id = feat.GetField('granule')
        if feat.GetGeometryRef().Intersects(cover_geom):
            granule_path = r'{}//{}.GRN{}.tif'.format(out_dir, id, granule_id)
            if os.path.exists(granule_path):
                print('File already exists %s' % granule_path)
                continue
            tpath = filter_dataset_by_col(vector_path, 'granule', granule_id, path_out=tempname('json'))
            tpath_meta = filter_dataset_by_col(raster_cover_path, 'id', id, path_out=tempname('json'))
            crop_bigraster_gdal(raster_path, tpath, granule_path)
            print('\n %i Granule written: %s.GRN%s' % (i, id, granule_id))
            # granule_meta_path = r'{}//{}.GRN{}.json'.format(out_dir, id, granule_id)
            # if os.path.exists(granule_meta_path):
                # print('File already exists %s' % granule_meta_path)
                # continue
            # granule_metadata_json(tpath, tpath_meta, granule_meta_path, granule_path)
            # json_fix_datetime(granule_meta_path)
            # print('%i Granule metadata written: %s.GRN%s \n' % (i, id, granule_id))