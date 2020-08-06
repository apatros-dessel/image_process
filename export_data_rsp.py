# -*- coding: utf-8 -*-

from geodata import *
import shutil

dir_in = r'\\172.21.195.2\FTP-Share\ftp\images0\102_2020_265'        # Путь к папке с исходными данными
dir_out = r'd:\digital_earth\s3'    # Путь к месту хранения конечных данных
json_in = r'\\172.21.195.2\FTP-Share\ftp\images0\102_2020_265\102_2020_265_fullcover.json' # Путь к векторному файлу покрытия
granules_path = r'D:\digital_earth\granules_grid.shp' # Путь к векторному файлу гранул
# id_xls = r'C:\Users\admin\Desktop\granules_selected.xls' # Путь к таблице xls с перечнем id отобранных снимков
overwrite = False

# Change Resursp granule name to format we use at S3/earth-services
def rename_granule(n_old):
    # 39028833_RP1_20115_03_GEOTON_20170128_065341_065415.SCN1.PMS.L2.tif
    grn, id = n_old.split('_RP')
    n_new = 'RP%s.GRN%s' % (id, grn)
    return n_new

# Change json cover geometry taking it from geometry file by id
def set_granule_geom(cover_path, granules_path, id, colname):
    d_gran, l_gran = get_lyr_by_path(granules_path)
    for feat_gran in l_gran:
        if feat_gran.GetField(colname)==id:
            din, lin = get_lyr_by_path(cover_path, 1)
            feat = lin.GetNextFeature()
            geom1 = feat.GetGeometryRef()
            geom2 = feat_gran.GetGeometryRef()
            feat.SetGeometry(geom1.Intersection(geom2))
            lin.SetFeature(feat)
            din = None
            return 0
    print('No granule geometry found for %s' % id)
    return 1


ms_list = folder_paths(dir_in, 1, 'tif',filter_folder=['brak'])
path_dict = {'ms': dir_in, 'json': json_in}
#scroll(ms_dict)

err_list = []

for i, pin in enumerate(ms_list):
    f, n, e = split3(pin)

    # Make new name
    try:
        name = rename_granule(n)
    except:
        print('New name not found for: %s' % n)
        err_list.append(n)
        continue

    id_dir = ('%s\\%s' % (dir_out, name))
    id = name.split('.GRN')[0]
    suredir(id_dir)

    # Add granule source data
    try:
        if check_exist(fullpath(id_dir, name, e), overwrite, 1):
            print('%i -- file exists -- %s.%s' % (i, name, e))
        else:
            shutil.copyfile(pin, fullpath(id_dir, name, e))
    except:
        err_list.append('%s.tif' % name)

    # Add json cover data
    try:
        if check_exist(fullpath(id_dir, name, 'json'), overwrite, 1):
            print('%i -- file exists -- %s.json' % (i, name))
        else:
            filter_dataset_by_col(path_dict['json'], 'id', id, path_out=fullpath(id_dir, name, 'json'))
            set_granule_geom(fullpath(id_dir, name, 'json'), granules_path, re.search('\d+$', name).group(), 'granule')
            json_fix_datetime(path_out) # Fixes error with Python OGR datetime data
    except:
        err_list.append('%s.json' % name)

    # Add quicklook
    try:
        temp_ql = tempname('tif')
        if check_exist(fullpath(id_dir, name + '.QL', e), overwrite, 1):
            print('%i -- file exists -- %s.QL.tif' % (i, name))
        else:
            MakeQuicklook(fullpath(id_dir, name, e), temp_ql, 3857, pixelsize=30, overwrite=False)
            RasterToImage3(temp_ql,
                           fullpath(id_dir, name + '.QL', e),
                           method=2,
                           band_limits=[(0.01, 0.998), (0.01, 0.998), (0.01, 0.998)],
                           gamma=0.85,
                           exclude_nodata=True,
                           enforce_nodata=0,
                           band_order=[1, 2, 3],
                           GaussianBlur=False,
                           reprojectEPSG=3857,
                           reproject_method=gdal.GRA_Lanczos,
                           compress='DEFLATE',
                           overwrite=False,
                           alpha=True)
            os.remove(temp_ql)
    except:
        err_list.append('%s.QL.tif' % name)

    # Add small image
    # QuicklookImage(fullpath(id_dir, name + '.QL', e), fullpath(id_dir, name + '.IMG', e))
    try:
        if check_exist(fullpath(id_dir, name + '.IMG', e), overwrite, 1):
            print('%i -- file exists -- %s.IMG.tif' % (i, name))
        else:
            QuicklookImage(fullpath(id_dir, name + '.QL', e), fullpath(id_dir, name + '.IMG', e))
    except:
        err_list.append('%s.IMG.tif' % name)

    print('%i Scene written: %s' % (i+1, name))

    # break


if len(err_list) > 0:
    for id in err_list:
        print(id)
    print('%i ERRORS FOUND' % len(err_list))
else:
    print('SUCCESS')
