# -*- coding: utf-8 -*-
from __future__ import print_function
__author__ = 'factory'
__version__ = "1.0.0"

import os, sys, re, time

import subprocess
import numpy as np
from tools import *
from geodata import copydeflate, SaveRasterBands

init_image = None
final_image = None
input_folder = r'e:\rks\rucode\new3_3\reproject' # Путь к исходным растровым данным
output_folder = r'e:\rks\rucode\new3_3\composit' # Путь для сохранения итоговых композитов
bands_order = [1, 2, 3, 4, 1, 2, 3, 4] # Порядок каналов; для обработки Planet использовать [3,2,1,4,3,2,1,4]
images_order = ['i','i','i','i','f','f','f','f'] # Порядок изображений для отбора каналов (4 с первого снимка, 4 с последнего)
path2xls = r'e:\rks\rucode\new3_3\composit\composit.xls' # Путь к таблице с названиями файлов для коррегистрации, указанных соответственно в колонках 'old' и 'new'; в колонке 'composit' должно быть указано уникальное имя конечного файла (расширение можно не указывать)

def Usage():
    print(
       """
Tool for KANOPUS L2 APOI change detection (composit builder).
init_image_file final_image_file output_folder
[-io input images order][-bo input bands order]
init_image_file - init image file (i)
final_image_file - final image file (f)
output_folder - output folder
[-io] - input images order ('f,i,f' by default)
[-bo] - input bands order ('1,1,2' by default)
      """)
    sys.exit(1)

try:
    from pci.pansharp import *
    from pci.fexport import *
except:
    print('')
    print('PCI GEOMATICA not available.')
    print('')
    sys.exit(1)

try:
    import gdal, ogr, osr, gdalconst
except:
    print('')
    print('GDAL lib not available.')
    print('')
    sys.exit(1)

def runcmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(1)
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()

def GeoTiffSetNodata(fname, value_nodata):
    ds = gdal.Open ( fname, gdalconst.GA_Update )
    if ds is not None:
        band = ds.GetRasterBand(1)
        band.SetNoDataValue(value_nodata)
        band.FlushCache()
        band = None
        ds = None

def BuildActiveAreaMask(images, bands):
        mask=np.ones((images[0].RasterYSize, images[0].RasterXSize), dtype=np.int8)
        for band in bands:
            band_data=images[0].GetRasterBand(band).ReadAsArray().astype(np.uint16)
            mask[band_data==0]=0
            band_data=images[1].GetRasterBand(band).ReadAsArray().astype(np.uint16)
            mask[band_data==0]=0
        return mask

def ImageProperties(ifile):
    ds = gdal.Open ( ifile, gdalconst.GA_ReadOnly )
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]
    template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    r1 = {'minx': minx, 'miny': miny, 'maxx':maxx, 'maxy':maxy}
    wkt = template % r1
    srs=osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjectionRef())
    ds = None
    return wkt, int(srs.GetAttrValue("AUTHORITY", 1)), srs, gt

def pci_auto_coregistration(i_image, reference_image, geo_correct_image, in_match_chan = [1], ref_match_chan = [1], bxpxsz="2.1", polyorder=[1], reject = [5, 1, 1], tresh=[0.88]):
    try:
        from pci.link import link
        from pci.autogcp2 import autogcp2
        from pci.gcprefn import gcprefn
        from pci.polymodel import polymodel
        from pci.ortho2 import ortho2
        ingest_link_file = i_image.split('.')[0]+'.pix'

        if os.path.exists(ingest_link_file):
            os.remove(ingest_link_file)

        link( i_image, ingest_link_file, [] )
        increase_radius = 0
        num_gcps = [0]

        while ((int(num_gcps[0]) > 6) == True) !=  ((increase_radius < 100) == True):
            search_radius = [15+increase_radius]
            smplsrc="GRID:256"
            algo="FFTP"
            gcp_seg = autogcp2( ingest_link_file, in_match_chan, u"", [], [], reference_image, ref_match_chan,
                                u"", [], [], u"", u"", [], smplsrc, algo, search_radius, u"", tresh, u"", num_gcps )
            increase_radius+=15
            tresh=[tresh[0]-0.01]

            if increase_radius>60:
                break

        reject = reject
        refined_gcp_seg = []
        out_stats = []
        gcprefn( ingest_link_file, [gcp_seg[-1]], [], [], "POLY", [], reject, "NO", refined_gcp_seg, out_stats )
        polymodel( ingest_link_file, [refined_gcp_seg[0]], polyorder, [] )
        ortho2(ingest_link_file, [], [], [], "", geo_correct_image, "TIF", "", [], "", "", "",
                "", [], "", "", bxpxsz, "", "", [], [], "", "", [], "", [], "")

        if os.path.exists(ingest_link_file):
            os.remove(ingest_link_file)

        return out_stats

    except:
        return []

def copydeflate(path_in, path_out, bigtiff = False, tiled = False):
    ds_in = gdal.Open(path_in)
    if ds_in is None:
        print('Cannot open file {}'.format(path_in))
        return 1
    dir_out = os.path.split(path_out)[0]
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    options = ['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9']
    if bigtiff:
        options.append('BIGTIFF=YES')
    if tiled:
        options.append('TILED=YES')
    driver = gdal.GetDriverByName('GTiff')
    ds_out = driver.CreateCopy(path_out, ds_in, options=options)
    ds_out = None
    print('File written {}'.format(path_out))
    return 0

# Import data from xls
def xls_to_dict(path2xls, sheetnum=0):
    rb = xlrd.open_workbook(path2xls)
    sheet = rb.sheet_by_index(sheetnum)
    keys = sheet.row_values(0)[1:]
    xls_dict = OrderedDict()
    for rownum in range(1, sheet.nrows):
        rowdata = OrderedDict()
        row = sheet.row_values(rownum)
        for key, val in zip(keys, row[1:]):
            rowdata[key] = val
        xls_dict[row[0]] = rowdata
    return xls_dict

# Searches filenames according to template and returns a list of full paths to them
def folder_paths(path, files = False, extension = None, id_max=10000):
    if os.path.exists(path):
        if not os.path.isdir(path):
            path = os.path.split(path)[0]
        path_list = [path]
        path_list = [path_list]
    else:
        print('Path does not exist: {}'.format(path))
        return None
    id = 0
    export_files = []
    while id < len(path_list) < id_max:
        for id_fold, folder in enumerate(path_list[id]):
            fold_, file_ = fold_finder(folder)
            if fold_ != []:
                path_list.append(fold_)
            if extension is None:
                export_files.extend(file_)
            else:
                for f in file_:
                    if f.endswith('.{}'.format(extension)):
                        export_files.append(f)
        id += 1
    if len(path_list) > id_max:
        raise Exception('Number of folder exceeds maximum = {}'.format(id_max))
    if files:
        return export_files
    export_folders = unite_multilist(path_list)
    return export_folders, export_files

# Returns a list of two lists: 0) all folders in the 'path' directory, 1) all files in it
def fold_finder(path):
    dir_ = os.listdir(path)
    fold_ = []
    file_ = []
    for name in dir_:
        full = path + '\\' + name
        if os.path.isfile(full):
            file_.append(full)
        else:
            fold_.append(full)
    return [fold_, file_]

# Unite all lists in a list of lists into a new list
def unite_multilist(list_of_lists):
    if len(list_of_lists) == 0:
        return []
    full_list = copy(list_of_lists[0])
    for list_ in list_of_lists[1:]:
        if isinstance(list_, list):
            full_list.extend(list_)
        else:
            print('Error: object is not a list: {}'.format(list_))
    return full_list

def scroll(obj, print_type=True, header=None):
    if header is not None:
        print(header)
    elif print_type:
        print('Object of {}:'.format(type(obj)))
    if hasattr(obj, '__iter__'):
        if len(obj) == 0:
            print('  <empty>')
        elif isinstance(obj, (dict, OrderedDict)):
            for val in obj:
                print('  {}: {}'.format(val, obj[val]))
        else:
            for val in obj:
                print('  {}'.format(val))
    else:
        print('  {}'.format(obj))

xls_data = xls_to_dict(path2xls)

test = xls_data

init_image_list = []
final_image_list = []
composit_image_list = []
channels_list = []

for i in xls_data.keys():
    test = xls_data[i]
    # scroll(test)
    init_test = test['old']#.replace('.PMS','.MS')
    final_test = test['new']#.replace('.PMS','.MS')
    for path in folder_paths(input_folder, 1, 'tif'):
        if init_test in path:
            init_image_list.append(path)
        if final_test in path:
            final_image_list.append(path)
    composit_image_list.append(fullpath(output_folder, test['composit'], 'tif'))

argv = sys.argv

if argv is None:
    sys.exit(1)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

'''
# Parse command line arguments.
i = 1
while i < len(argv):
    arg = argv[i]

    if init_image is None:
        init_image = argv[i]

    elif final_image is None:
        final_image = argv[i]

    elif output_folder is None:
        output_folder = argv[i]

    elif arg == '-io':
        i = i + 1
        images_order = [j for j in argv[i].split(',')]

    elif arg == '-bo':
        i = i + 1
        bands_order = [int(j) for j in argv[i].split(',')]

    else:
        Usage()

    i = i + 1

if init_image is None:
    Usage()

if final_image is None:
    Usage()

if output_folder is None:
    Usage()
'''

error_list = []

for init_image, final_image, composit_image in zip(init_image_list, final_image_list, composit_image_list):

        imI_wkt, imI_epsg, imI_srs, imI_gt = ImageProperties(init_image)
        imF_wkt, imF_epsg, imF_srs, imF_gt = ImageProperties(final_image)
        imI_geom = ogr.CreateGeometryFromWkt(imI_wkt, imI_srs)
        imF_geom = ogr.CreateGeometryFromWkt(imF_wkt, imF_srs)
        intersection_geom = imI_geom.Intersection(imF_geom)
        overlap = round(100 * intersection_geom.Area() / imI_geom.Area(), 2)

        if overlap>0:
            if os.path.exists(composit_image):
                print('File already exists: {}'.format(composit_image))
                continue
            t_composit_image = '%s_t.tif' % composit_image[:-4]
            t_corregistred_image = '%s_t_corrected.tif' % composit_image[:-4]
            init_image_sname = os.path.basename(init_image)
            final_image_sname = os.path.basename(final_image)

            try:
                
                if not os.path.exists(t_corregistred_image):
                    pci_auto_coregistration(final_image, init_image, t_corregistred_image,
                        in_match_chan = [bands_order[images_order.index('f')]],
                        ref_match_chan = [bands_order[images_order.index('i')]],
                        bxpxsz=str(imI_gt[1]), polyorder=[1], reject = [5, 1, 1], tresh=[0.88])
                
                if os.path.exists(t_corregistred_image):
                    imC_wkt, imC_epsg, imC_srs, imC_gt = ImageProperties(t_corregistred_image)
                    imC_geom = ogr.CreateGeometryFromWkt(imC_wkt, imC_srs)
                    intersection_geom = imI_geom.Intersection(imC_geom)
                    ulx, lrx, lry, uly = intersection_geom.GetEnvelope()
                    bbox=[str(ulx),str(uly),str(lrx),str(lry)]
                    TemporyInitImage=t_composit_image.replace('.tif','_init.VRT')
                    TemporyFinImage=t_composit_image.replace('.tif','_final.VRT')
                    cmd='gdal_translate -of VRT -projwin {0} {1} {2}'.format (' '.join(bbox), init_image, TemporyInitImage)
                    runcmd(cmd)
                    cmd='gdal_translate -of VRT -projwin {0} {1} {2}'.format(' '.join(bbox), t_corregistred_image, TemporyFinImage)
                    runcmd(cmd)
                    imageI_sub=gdal.Open( TemporyInitImage, gdalconst.GA_ReadOnly )
                    imageF_sub=gdal.Open( TemporyFinImage, gdalconst.GA_ReadOnly )
                    used_bands = []
                    
                    for b in bands_order:
                        if b not in used_bands:
                            used_bands+=[b]

                    mask = BuildActiveAreaMask([imageI_sub, imageF_sub], bands_order)

                    if not os.path.exists(t_composit_image):
                        dst_ds = gdal.GetDriverByName("GTiff").Create( t_composit_image , mask.shape[1], mask.shape[
                            0],  len(bands_order), gdalconst.GDT_UInt16)
                        dst_ds.SetGeoTransform( imageI_sub.GetGeoTransform() )
                        dst_ds.SetProjection( imageI_sub.GetProjection() )

                        for image, band, band_index in zip(images_order, bands_order, range(1, len(bands_order)+1)):

                            if image=='f':
                                band_data = imageF_sub.GetRasterBand(band).ReadAsArray().astype(np.uint16)

                            elif image=='i':
                                band_data = imageI_sub.GetRasterBand(band).ReadAsArray().astype(np.uint16)

                            band_data[mask==0]=0
                            dst_ds.GetRasterBand(band_index).WriteArray(band_data)

                        dst_ds=None
                        GeoTiffSetNodata(t_composit_image, 0)

                    imageF_sub = None
                    imageI_sub = None

                    print(t_composit_image, composit_image)
                    copydeflate(t_composit_image, composit_image)

                    SaveRasterBands(composit_image, [5,1,6], composit_image[:-4]+'_3CH.tif', options={'compress': 'DEFLATE'}, overwrite=False)

                    for i_f in [TemporyInitImage, TemporyFinImage, t_corregistred_image, t_composit_image]:
                        if os.path.exists(i_f):
                            os.remove(i_f)

                else:
                    print('Corregistration error')

            except:
                print('Error making file {}'.format(composit_image))
                error_list.append(composit_image)

        else:
            print('Overlaping error - %s '%str(overlap))

scroll(error_list, header='Errors found')
