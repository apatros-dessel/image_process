# -*- coding: utf-8 -*-

from geodata import *
from shutil import copyfile

path_in = r'e:\test' # Путь к исходным сценам Ресурс-П
raster_fullcover = r'\\172.21.195.2\FTP-Share\ftp\images\region69\RP_Tver_cover.json'      # Путь к файлу покрытия Ресурс-П
aoi_path =  None#r'\\172.21.195.2\FTP-Share\ftp\!region_shows\krym\Эко\Свалки\KRYM_SIMFEROPOLSKIY_border.shp'
vector_path = r'\\172.21.195.2\thematic\Sadkov_SA\tiles_gshmsa.json'                                         # Путь к файлу сетки гранул
out_dir = r'\\172.21.195.2\FTP-Share\ftp\images\region69'                                                             # Путь к готовым гранулам
ms2pms = True

def crop_bigraster_gdal(path_in, path_vec, path_out):
    command = "gdalwarp -of GTiff -cutline {path_vec} -crop_to_cutline -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 {path_in} {path_out} -co NUM_THREADS=ALL_CPUS".format(path_vec=path_vec, path_in=path_in, path_out=path_out)
    os.system(command)

def resurs_granule_index(filename):
    satid, loc1, sentnum, resurs, date, num1, ending = undersplit = filename.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    lvl = dotsplit[3]
    if 'PMS' in dotsplit:
        lvl += 'PMS'
    granule = dotsplit[-1]
    scn_num = scn.replace('SCN', '')
    if not granule.startswith('GRN'):
        granule = ('GRN' + granule)
    indexname = '{}-{}-{}{}{}-{}'.format(satid, date, loc1, scn_num, granule, lvl)
    return indexname

def granule_metadata_json(path_granule, path_cover_meta, path_out, raster_path, ms2pms = False):
    # Get input data
    shutil.copyfile(path_cover_meta, path_out)
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
    if ms2pms:
        tile_id = tile_id.replace('.MS', '.PMS')
        fout.SetField('type', 'PMS')
        rgr = gdal.Open(raster_path)
        if rgr:
            fout.SetField('rows', rgr.RasterYSize)
            fout.SetField('cols', rgr.RasterXSize)
            transform = rgr.GetGeoTransform()
            fout.SetField('x_size', float(transform[1]))
            fout.SetField('y_size', float(-transform[-1]))
    fout.SetField('id', tile_id)
    fout.SetField('id_neuro', resurs_granule_index(tile_id))
    fout.SetField('id_s', fout.GetField('id_neuro').split('-')[2])
    lout.SetFeature(fout)
    dout = None

suredir(out_dir)

loop = OrderedDict()

for fpath in folder_paths(path_in, 1, 'tif'):
    f = os.path.basename(fpath)
    if re.search(r'^r.*\.pms\.l2\.tif$', f.lower(), flags=0):
        id, ext = os.path.splitext(f)
        if ms2pms:
            filter_id = id.replace('.PMS.','.MS.')
        else:
            filter_id = id
        json_ = filter_dataset_by_col(raster_fullcover, 'id', filter_id, path_out=tempname('json'))
        ds_meta, lyr_meta = get_lyr_by_path(json_)
        if lyr_meta:
            if lyr_meta.GetFeatureCount()!=0:
                loop[id] = {'tif': fpath}
                # loop[id]['json'] = filter_dataset_by_col(raster_fullcover, 'id', id, path_out=tempname('json'))
                loop[id]['json'] = json_
                print('Lyr created: %s' % filter_id)
            else:
                print('WARNING: Empty lyr %s' % filter_id)
        else:
            print('WARNING: Lyr not created %s' % filter_id)

for i, id in enumerate(loop):

    raster_path = loop[id].get('tif')
    raster_cover_path = loop[id].get('json')

    if ms2pms:
        filter_id = id.replace('.PMS.', '.MS.')
    else:
        filter_id = id

    if None in (raster_path, raster_cover_path):
        continue

    crop_ds, crop_lyr = get_lyr_by_path(vector_path)
    cover_ds, cover_lyr = get_lyr_by_path(raster_cover_path)
    cover_feat = cover_lyr.GetNextFeature()
    cover_geom = cover_feat.GetGeometryRef()

    for feat in crop_lyr:
        granule_id = feat.GetField('granule')
        if feat.GetGeometryRef().Intersects(cover_geom):
            if aoi_path:
                ds_aoi, lyr_aoi = get_lyr_by_path(aoi_path)
                if lyr_aoi:
                    aoi_feat = lyr_aoi.GetNextFeature()
                    aoi_geom = aoi_feat.GetGeometryRef()
                    if not feat.GetGeometryRef().Intersects(aoi_geom):
                        continue
            tpath = filter_dataset_by_col(vector_path, 'granule', granule_id, path_out=tempname('json'))
            tpath_meta = filter_dataset_by_col(raster_cover_path, 'id', filter_id, path_out=tempname('json'))
            ds_meta, lyr_meta = get_lyr_by_path(tpath_meta)
            if lyr_meta:
                if lyr_meta.GetFeatureCount()==0:
                    continue
                granule_path = r'{}//{}.GRN{}.tif'.format(out_dir, id, granule_id)
                if os.path.exists(granule_path):
                    print('File already exists: %s' % granule_path)
                else:
                    crop_bigraster_gdal(raster_path, tpath, granule_path)
                    print('\n %i Granule written: %s.GRN%s' % (i, id, granule_id))
                granule_meta_path = r'{}//{}.GRN{}.json'.format(out_dir, id, granule_id)
                granule_metadata_json(tpath, tpath_meta, granule_meta_path, granule_path, ms2pms=ms2pms)
                json_fix_datetime(granule_meta_path)
                print('%i Granule metadata written: %s.GRN%s \n' % (i, id, granule_id))
            else:
                print('ERROR: lyr_meta not found: %s' % id)
