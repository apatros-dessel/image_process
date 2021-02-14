# -*- coding: utf-8 -*-

from geodata import *
from image_processor import process
import argparse

parser = argparse.ArgumentParser(description='Path to vector file')
parser.add_argument('-i', default=None, dest='txt_ids', help='Files id list, if necessary')
parser.add_argument('-d', default=None, dest='dir_out', help='Output directory if different from dir_in')
parser.add_argument('-o', default=True, dest='preserve_original', help='Preserve original files')
parser.add_argument('-r', default=False, dest='make_rgb', help='Create RGB files')
parser.add_argument('-v', default=None, dest='json_cover', help='Vector cover path')
parser.add_argument('-g', default=None, dest='vector_granule_path', help='Path to vector granule files')
parser.add_argument('-m', default=False, dest='ms2pms', help='Convert MS files to PMS')
parser.add_argument('-b', default=False, dest='invert_red_blue', help='Change bands order from 1.2.3 to 3.2.1')
parser.add_argument('dir_in', help='Path to vector file')
args = parser.parse_args()
dir_in = args.dir_in
dir_out = args.dir_out
txt_ids = args.txt_ids
preserve_original = args.preserve_original
make_rgb = boolstr(args.make_rgb)
json_cover = args.json_cover
vector_granule_path = args.vector_granule_path
ms2pms = args.ms2pms
invert_red_blue = args.invert_red_blue

if dir_out is None:
    dir_out = dir_in

# dir_in = r'\\172.21.195.2\FTP-Share\ftp\planet_imgs\LES\archive\Ostashkovskoe_lesnichestvo\Case1\ostashkovskoe_2020may_cut1_PSScene4band_b21bb6c5-2af9-439c-912b-cc9a8492c0b2'
# txt_ids = None#r'd:\digital_earth\KV_Tatarstan\kv_ids.txt'
# dir_out = r'd:\rks\PL_new_201023\ostashkovskoe_2020may_cut1'
preserve_original = True
make_rgb = False

vector_granule_path = r'\\172.21.195.2\FTP-Share\ftp\images\granules_grid.shp'
ms2pms = False
invert_red_blue = False

if json_cover is None:
    json_cover = tempname('json')
    process().input(dir_in, skip_duplicates=False).GetCoverJSON(json_cover)
    pass

names_tmpt = {
    'sentinel': ('^S2[AB]_MSI.+\d$', [3,2,1]),
    'sentinel_rgbn': ('^S2[AB].+RGBN$', [1,2,3]),
    'planet': ('.*AnalyticMS(_SR)?$', [3,2,1]),
    'planet_neuro': ('IM4-PLN.*', [1,2,3]),
    'kanopus': ('KV.+PMS.+L2$', [1,2,3]),
    # 'resursp': ('RP.+L2$', [1,2,3]),
    'resursp-grn': ('RP.+PMS\.L2\.GRN\d+$', [1,2,3]),
    'resursp-grn_new': ('\d_+RP.+PMS\.L2$', [1,2,3]),
    'kanopus_new_ref': ('^fr.+KV.+$', [1,2,3]),
    'digital-globe': (r'\d+[A-Z]+\d+-.*P\d+$', [3,2,1]),
}

def valid_str(str_, tmpt_dict):
    # tmpt_list = obj2list(tmpt_list)
    for key in tmpt_dict:
        tmpt, band_list = tmpt_dict[key]
        if re.search(tmpt, str_):
            return band_list
    return False

def copymove(file_in, file_out, preserve_original):
    if file_in==file_out:
        print('ERROR: IN AND OUT PATHS ARE THE SAME')
    elif not os.path.exists(file_in):
        print('FILE NOT FOUND: %s' % file_in)
    elif os.path.exists(file_out):
        print('FILE ALREADY EXISTS: %s' % file_out)
    elif preserve_original:
        shutil.copyfile(file_in, file_out)
    else:
        shutil.move(file_in, file_out)

def get_pms_json(path_cover, path_out, pms_id, pms_raster_path=''):

    if os.path.exists(path_out):
        print('FILE EXISTS: %s' % path_out)
        return 1

    if not os.path.exists(path_cover):
        print('Cannot find path: {}'.format(path_cover))
        return 1

    ms_id = pms_id.replace('.PMS', '.MS')
    filter_dataset_by_col(path_cover, 'id', ms_id, path_out=path_out)

    pms_ds, pms_lyr = get_lyr_by_path(path_out, 1)

    if pms_lyr is None:
        print('FILE NOT FOUND: %s' % path_out)
        return 1
    elif len(pms_lyr)==0:
        print('EMPTY LAYER: %s' % path_out)
        pms_ds = None
        os.remove(path_out)
        return 1

    feat = pms_lyr.GetNextFeature()
    feat.SetField('id', pms_id)
    feat.SetField('id_neuro', feat.GetField('id_neuro') + 'PMS')
    feat.SetField('type', 'PMS')

    if os.path.exists(pms_raster_path):
        pms_data = gdal.Open(pms_raster_path)
    else:
        pms_data = None
    if pms_data is not None:
        feat.SetField('rows', int(pms_data.RasterYSize))
        feat.SetField('cols', int(pms_data.RasterXSize))
        trans = pms_data.GetGeoTransform()
        if trans:
            feat.SetField('x_size', float(trans[0]))
            feat.SetField('y_size', -float(trans[-1]))
        else:
            feat.SetField('x_size', None)
            feat.SetField('y_size', None)
    else:
        pan_id = pms_id.replace('.PMS', '.PAN')
        tpan_path = filter_dataset_by_col(path_cover, 'id', pan_id)
        pan_ds, pan_lyr = get_lyr_by_path(tpan_path)
        pan_feat = pan_lyr.GetNextFeature()
        feat.SetField('rows', int(pan_feat.GetField('rows')))
        feat.SetField('cols', int(pan_feat.GetField('cols')))
        feat.SetField('x_size', float(pan_feat.GetField('x_size')))
        feat.SetField('y_size', float(pan_feat.GetField('y_size')))
    # feat.SetField('area', None)

    pms_lyr.SetFeature(feat)

    pms_ds = None

    print('PMS data successfully written for for %s' % pms_id)

    return 0

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

def RenameGrn(n):
    split_ = n.split('_')
    return '%s.GRN%s' % ('_'.join(split_[1:]), split_[0])

def RenameSnt(n, json_cover, col_id = 'id'):
    ds_, lyr_ = get_lyr_by_path(json_cover)
    if lyr_:
        sat, date, tile, lvl, rgbn = n.split('_')
        for feat in lyr_:
            id = feat.GetField(col_id)
            id_vals = id.split('_')
            if (id_vals[0]==sat) and (id_vals[1][-3:]==lvl) and\
                    (id_vals[2][:8]==date) and (id_vals[-2]==tile):
                return id
    else:
        return n

def InvertRedBlueBands(file):
    f,n,e = split3(file)
    temp_file = fullpath(f,n+'__',e)
    ds_ = gdal.Open(file)
    if ds_:
        band_count = ds_.RasterCount
        if band_count>=3:
            band_order = list(range(1,band_count+1))
            band_order[0] = 3
            band_order[2] = 1
        res = SaveRasterBands(file, band_order, temp_file)
        if res==0:
            ds_ = None
            os.remove(file)
            copydeflate(temp_file, file)
            # shutil.rename(temp_file, file)
            os.remove(temp_file)

path_in_list = folder_paths(dir_in, files=True, extension='tif', filter_folder=['brak'])
names_in_list = flist(path_in_list, lambda x: split3(x)[1])

if txt_ids not in (None, ''):
    ids = open(txt_ids).read().split('\n')
else:
    ids = False

report = []
export_data = []

for i, path_in in enumerate(path_in_list):

    f, n, e = split3(path_in)

    band_order = valid_str(n, names_tmpt)

    if band_order:
        if ids:
            if n not in ids:
                print('%i -- file skipped: not in filter -- %s' % (i, n))
                continue
        if re.search(names_tmpt['resursp-grn_new'][0], n):
            n = RenameGrn(n)
        elif re.search(names_tmpt['sentinel_rgbn'][0], n):
            n = RenameSnt(n, json_cover)
        id_dir_out = fullpath(dir_out, n)
        suredir(id_dir_out)
        raster_out = fullpath(id_dir_out, n, e)
        if not os.path.exists(raster_out):
            copymove(path_in, raster_out, preserve_original)
            if invert_red_blue:
                if band_order==[3,2,1]:
                    InvertRedBlueBands(raster_out)
                    band_order=[1,2,3]
                    print('Inverted RED/BLUE: %s' % n)
        report.append(n)
        export_data.append(raster_out)

        # if make_rgb:
        if make_rgb:
            # Add RGB
            id_rgb = n + '.RGB'
            rgb_out = fullpath(id_dir_out, id_rgb, 'tif')
            rgb_in = fullpath(f,id_rgb,'tif')
            if os.path.exists(rgb_in):
                copymove(rgb_in, rgb_out, preserve_original)
            else:
                try:
                    RasterToImage3(raster_out,
                                             rgb_out,
                                             method=2,
                                             band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                                             gamma=0.80,
                                             exclude_nodata=True,
                                             enforce_nodata=0,
                                             band_order=band_order,
                                             GaussianBlur=False,
                                             # reprojectEPSG=3857,
                                             reproject_method=gdal.GRA_Bilinear,
                                             compress='DEFLATE',
                                             overwrite=False,
                                             alpha=True)
                except:
                    print('%i Error making RGB: %s' % (i, n))

            # Add quicklook
            id_ql = n + '.QL'
            ql_out = fullpath(id_dir_out, id_ql, e)
            ql_in = fullpath(f, id_ql, 'tif')
            if os.path.exists(ql_in):
                copymove(ql_in, ql_out, preserve_original)
            else:
                try:
                    MakeQuicklook(rgb_out, ql_out, 3857, pixelsize=30, overwrite=False)
                except:
                    print('{} Error making quicklook: {}'.format(i, n))

        else:
            # Add quicklook
            id_ql = n + '.QL'
            ql_out = fullpath(id_dir_out, id_ql, e)
            ql_in = fullpath(f,id_ql,'tif')
            if os.path.exists(ql_in):
                copymove(ql_in, ql_out, preserve_original)
            else:
                    try:
                        temp_ql = tempname('tif')
                        if check_exist(fullpath(id_dir_out, n + '.QL', e), False):
                            print('%i -- file exists -- %s.QL.tif' % (i, n))
                        else:
                            MakeQuicklook(raster_out, temp_ql, 3857, pixelsize=30, overwrite=False, method=gdal.GRA_NearestNeighbour)
                            RasterToImage3(temp_ql,
                                           fullpath(id_dir_out, n + '.QL', e),
                                           method=2,
                                           band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                                           gamma=0.80,
                                           exclude_nodata=True,
                                           enforce_nodata=0,
                                           band_order=band_order,
                                           GaussianBlur=False,
                                           # reprojectEPSG=3857,
                                           reproject_method=gdal.GRA_Bilinear,
                                           compress='DEFLATE',
                                           overwrite=False,
                                           alpha=True)
                            os.remove(temp_ql)
                            '''
                            for method in [gdal.GRA_NearestNeighbour, gdal.GRA_Average]:
                                MakeQuicklook(raster_out, temp_ql, 3857, pixelsize=30, overwrite=False, method=method)
                                RasterToImage3(temp_ql,
                                           fullpath(id_dir_out, n + '.QL.{}'.format(method), e),
                                           method=2,
                                           band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                                           gamma=0.80,
                                           exclude_nodata=True,
                                           enforce_nodata=0,
                                           band_order=band_order,
                                           GaussianBlur=False,
                                           # reprojectEPSG=3857,
                                           reproject_method=gdal.GRA_Bilinear,
                                           compress='DEFLATE',
                                           overwrite=False,
                                           alpha=True)
                                os.remove(temp_ql)
                            '''
                    except:
                        print('Error making QL: %s.QL.tif' % n)

        # Add image
        # try:
            # n_img = n + '.IMG'
            # path_img = +fullpath(id_dir_out, n_img, e)
            # QuicklookImage(path_ql, path_img)
            # print('IMG written: %s' % n_img)
        # except:
            # print('Error making IMG: %s' % n_img)

        # Copy json

        json_in = path_in.replace('.tif', '.json').replace('.TIF', '.json')
        json_out = fullpath(id_dir_out, n, 'json')
        if os.path.exists(json_in):
            if json_in.lower()!=json_out.lower():
                shutil.move(json_in, json_out)
                print('%i JSON written %s' % (i, n))
        elif os.path.exists(json_in.replace('.PMS.','.MS.')):
            get_pms_json(json_in.replace('.PMS.','.MS.'), json_out, n, pms_raster_path=path_in)
        elif json_cover:
            if not os.path.exists(json_out):
                # print(json_cover)
                if re.search(r'\.GRN\d+$', n) and vector_granule_path:
                    filter_id, granule_id = n.split('.GRN')
                    tpath = filter_dataset_by_col(vector_granule_path, 'granule', granule_id, path_out=tempname('json'))
                    tpath_meta = filter_dataset_by_col(json_cover, 'id', filter_id, path_out=tempname('json'))
                    ds_, lyr_ = get_lyr_by_path(tpath_meta)
                    if lyr_.GetFeatureCount()==1:
                        granule_metadata_json(tpath, tpath_meta, json_out, path_in, ms2pms=ms2pms)
                elif ms2pms:
                    get_pms_json(json_cover, json_out, n, pms_raster_path=path_in)
                else:
                    # scroll((json_cover, json_out, n))
                    filter_dataset_by_col(json_cover, 'id', n, path_out=json_out)
                if os.path.exists(json_out):
                    ds_out, lyr_out = get_lyr_by_path(json_out)
                    if lyr_out is None:
                        print('JSON metadata file not created: %s' % n)
                        ds_out = None
                        os.remove(json_out)
                    elif len(lyr_out)==0:
                        print('JSON metadata file is empty: %s' % n)
                        ds_out = None
                        os.remove(json_out)
                    else:
                        json_fix_datetime(json_out)
            else:
                print('%i -- file exists -- %s.json' % (i, n))

if report:
    TotalCover(fullpath(dir_out, 'scene_cover.json'), export_data)
    with open(fullpath(dir_out, 'scene_list.txt'), 'w') as txt:
        txt.write('\n'.join(report))
