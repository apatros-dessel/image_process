# -*- coding: utf-8 -*-

from geodata import *
from shutil import copyfile

path_in = r'\\172.21.195.2\FTP-Share\ftp\images\region82\RP1_38863_06_GEOTON_20200605_080512_080526.SCN2.PMS_d9dc7f44602c68945ece55b5d7e07e88ba55147c' # Путь к исходным сценам Ресурс-П
raster_fullcover = r'C:/Users/admin/Documents/vector_cover.json'      # Путь к файлу покрытия Ресурс-П
vector_path = r'd:\digital_earth\granules_grid.shp'                                         # Путь кфайлу сетки гранул
out_dir = r'e:\rks\resurs_granules_newnew'                                                             # Путь к готовым гранулам

def crop_bigraster_gdal(path_in, path_vec, path_out):
    command = "gdalwarp -of GTiff -cutline {path_vec} -crop_to_cutline -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 {path_in} {path_out} -co NUM_THREADS=ALL_CPUS".format(path_vec=path_vec, path_in=path_in, path_out=path_out)
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
    print(tile_id)
    fout.SetField('id', tile_id)
    fout.SetField('id_neuro', resurs_granule_index(tile_id))
    fout.SetField('id_s', fout.GetField('id_neuro').split('-')[2])
    # Get new metadata from raster
    # rgr = gdal.Open(raster_path)
    # fout.SetField('rows', rgr.GetYSize())
    # fout.SetField('cols', rgr.GetXSize())
    # Save new feature
    lout.SetFeature(fout)
    dout = None

suredir(out_dir)

loop = OrderedDict()

for fpath in folder_paths(path_in, 1):
    f = os.path.basename(fpath)
    if re.search(r'^r.*.l2\.tif$', f.lower(), flags=0):
        id, ext = os.path.splitext(f)
        loop[id] = {'tif': fpath}
        loop[id]['json'] = filter_dataset_by_col(raster_fullcover, 'id', id, path_out=tempname('json'))

# scroll(loop)

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
            tpath = filter_dataset_by_col(vector_path, 'granule', granule_id, path_out=tempname('json'))
            tpath_meta = filter_dataset_by_col(raster_cover_path, 'id', id, path_out=tempname('json'))
            granule_path = r'{}//{}.GRN{}.tif'.format(out_dir, id, granule_id)
            if os.path.exists(granule_path):
                print('File already exists: %s' % granule_path)
                continue
            crop_bigraster_gdal(raster_path, tpath, granule_path)
            print('\n %i Granule written: %s.GRN%s' % (i, id, granule_id))
            granule_meta_path = r'{}//{}.GRN{}.json'.format(out_dir, id, granule_id)
            granule_metadata_json(tpath, tpath_meta, granule_meta_path, granule_path)
            json_fix_datetime(granule_meta_path)
            print('%i Granule metadata written: %s.GRN%s \n' % (i, id, granule_id))