# -*- coding: utf-8 -*-

from image_processor import *
import gdal
import osr

path_list = [
    # r'C:\sadkov\rzd\!disk_20191205\Tinguta\OF'.encode('cp1251'),
    # r'C:\sadkov\rzd\!disk_20191205\Reutov\OF',
    # r'C:\sadkov\rzd\!disk_20191205\Severobaikalsk\OF',
    # r'c:\sadkov\rzd\disk_backup\Reutov',
    # r'c:\sadkov\rzd\disk_backup\Reutov\remastering',
    # r'c:\sadkov\rzd\disk_backup\Severobaikalsk\New_ortho',
    # r'c:\sadkov\rzd\disk_backup\Severobaikalsk\ortho',
    # r'c:\sadkov\rzd\disk_backup\Tinguta\LZW',
    # r'c:\sadkov\rzd\disk_backup\Tinguta\Uncompressed',
    # r'c:\sadkov\rzd\disk_backup\replace',
    r'c:\sadkov\rzd\fin3\Tinguta',
    r'c:\sadkov\rzd\fin3\Severobaikalsk',
    r'c:\sadkov\rzd\fin3\Reutov',
    # r'c:\sadkov\rzd\fin'
]

output_path = r'c:\sadkov\rzd\fin3'

path2raster = r'c:\sadkov\toropez\planet\20190516\2367219_3665010_2019-05-16_1011\2367219_3665010_2019-05-16_1011_BGRN_Analytic.tif'
path2export = r'C:\sadkov\playground\test\image.tif'
path2alpha = r'C:\sadkov\playground\test\image_alpha.tif'

t = datetime.now()
# geodata.RasterToImage(path2raster, path2export, method = 0, band_limits=(0.02, 0.995), band_order=[3,2,1], compress='LERC_DEFLATE', enforce_nodata=0, gamma=0.85, alpha=True)
# geodata.alpha(path2export, path2alpha)

driver = gdal.GetDriverByName('GTiff')

report = OrderedDict()

for path in path_list:
    file_list = os.listdir(path)
    for file in file_list:
        if file.endswith('.tif'):
            abspath = fullpath(path.decode('cp1251'), file)
            s_ds = gdal.Open(abspath)
            if s_ds is not None:

                image_line = OrderedDict()

                res = ''

                try:
                    geotrans = s_ds.GetGeoTransform()
                    proj = osr.SpatialReference()
                    proj.ImportFromWkt(s_ds.GetProjection())
                    print('{} - {}x{}, {}'.format(file, round(geotrans[1], 2), - round(geotrans[5], 2), s_ds.GetRasterBand(1).DataType), proj.ExportToProj4())
                    export = fullpath(output_path, file)

                    image_line['data_type'] = s_ds.GetRasterBand(1).DataType
                    image_line['pixe_size'] = '{}x{}'.format(round(geotrans[1], 2), - round(geotrans[5], 2))
                    image_line['proj'] = proj.ExportToProj4()

                    # if os.path.exists(export):
                        # export = export[:-4] + '_' + str(path_list.index(path)) + '.tif'
                        # raise FileExistsError
                    # t2 = datetime.now()
                    # if s_ds.GetRasterBand(1).DataType not in (0,1):
                        # t_ds = geodata.ds(export, copypath=abspath, options={'dt':1, 'compress': 'LZW'}, editable=True)
                        # gdal.ReprojectImage(s_ds, t_ds, None, None, gdal.GRA_Lanczos)
                        # t_ds = None
                    # else:
                        # t_ds = driver.CreateCopy(export, s_ds, options = ['COMPRESS=LZW'])
                    # t_ds = None
                    # print('Saved: {} for {}'.format(file, datetime.now() - t2))
                    # res = 'saved'
                except FileExistsError:
                    print('File already exists: {}'.format(export))
                    # res = 'file_exists'
                except:
                    print('Failed to save: {}'.format(export))
                    # res = 'error'

                # image_line['result'] = res
                report[file] = image_line
                image_line = None


print(datetime.now() - t)

dict_to_xls(r'c:\sadkov\rzd\fin3\report.xls', report)


