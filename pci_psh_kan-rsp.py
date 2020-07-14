# -*- coding: utf-8 -*-
from __future__ import print_function
__author__ = 'factory'
__version__ = "1.0.0"

import os, sys, re, time
from datetime import datetime
from geodata import *

try:
    from pci.pansharp import *
    from pci.fexport import *
except:
    print('\nPCI GEOMATICA not available.\n')
    sys.exit(1)

try:
    import gdal
    use_deflate = True
except:
    print('Error importing GDAL, cannot apply deflate')
    use_deflate = False

data_source_folder = r'\\tt-nas-archive\NAS-Archive-2TB-5\na-va\102_2020_91'   # Путь к исходным данным Канопус/Ресурс-П PAN+MS
output_folder = r'\\tt-nas-archive\NAS-Archive-2TB-7\kan-pms\sverdlovsk' # Путь к конечным паншарпам
filter_path = r'e:\DigitalEarth_QL_reports\Kemerovo_selected.xls' # Путь к файлу с перечнем сцен для обработки (txt или xls)

bands = [1,2,3,4]
bands_ref = [1,2,3,4]
enhanced = "YES"

def Usage():
    print(
       """
Tool for KANOPUS L2 pansharpening.
data_source_folder output_folder
[-bands input bands type][-refbands reference bands][-ne]
data_source_folder - input folder with satimagery
output_folder - output folder
[-bands] - Input bands ('1,2,3,4' by default)
[-refbands] - Input reference bands ('1,2,3,4' by default)
[-ne] - Pansharpening without the color enhancement operation
      """)
    sys.exit(1)

def get_filter_names(filter_path, xlscolname=None, txtsep=';'):
    if os.path.exists(filter_path):
        if filter_path.endswith('xls'):
            filter_xls = xls_to_dict(filter_path)
            if xlscolname is None:
                filter_names = filter_xls.keys()
            else:
                filter_names = colfromdict(filter_xls, 'new', True)
        elif filter_path.endswith('txt'):
            with open(filter_path) as txt:
                filter_names = txt.read().split(txtsep)
        else:
            print('Unreckognized filter path extension: need .xls or .txt')
            filter_names = None
    else:
        print('File not found: {}'.format(filter_path))
        filter_names = None
    if filter_names is not None:
        for i, name in enumerate(filter_names):
            filter_names[i] = name.replace('.MS.', '.PMS.').replace('.PAN.', '.PMS.')
    return filter_names

# Make pansharpened image
def image_psh(ms, pan, psh, bands, bands_ref, enhanced):
    fili = ms
    dbic = bands
    dbic_ref = bands_ref
    fili_pan = pan
    dbic_pan = [1]
    filo = psh.replace('.tif','.pix')
    dboc = dbic
    enhance = enhanced     # apply the color enhancement operation
    nodatval = [0.0]       # zero-valued pixels in any input image are excluded from processing
    poption = "OFF"        # resampling used to build pyramid overview images
    pansharp(fili, dbic, dbic_ref, fili_pan, dbic_pan, filo, dboc, enhance, nodatval, poption)
    fili = filo
    filo = psh
    dbiw = []
    dbic = dbic
    dbib = []
    dbvs = []
    dblut = []
    dbpct = []
    ftype =	"TIF"
    foptions = "TILED256"
    fexport( fili, filo, dbiw, dbic, dbib, dbvs, dblut, dbpct, ftype, foptions )
    if os.path.exists(filo):
        for file in (fili, filo+'.pox'):
            if os.path.exists(file):
                os.remove(file)

def pms_iter(data_source_folder,
             output_folder,
             bands = [1,2,3],
             bands_ref = [1,2,3],
             enhanced = 'YES',
             use_deflate = False,
             filter_names = None,
             trynum = 20):

    # Parse command line arguments.
    i = 1
    while i < len(argv):
        arg = argv[i]
        if data_source_folder is None:
            data_source_folder = argv[i]
        elif output_folder is None:
            output_folder = argv[i]
        elif arg == '-bands':
            i = i + 1
            bands = [int(j) for j in argv[i].split()]
        elif arg == '-refbands':
            i = i + 1
            bands_ref = [int(j) for j in argv[i].split()]
        elif arg == '-ne':
            enhanced = "NO"
        else:
            Usage()
        i = i + 1

    if data_source_folder is None:
        # Usage()
        data_source_folder=os.getcwd()
    if output_folder is None:
        output_folder=data_source_folder + r'\pms'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    loop={}

    for filepath in folder_paths(data_source_folder, files = True, extension='tif'):

        root, f = os.path.split(filepath)

        # Kanopus
        if re.search(r'^k.*.l2\.tif$', f.lower(), flags=0):
            product_path = root
            sat, orbit, marshrut, part, satname, imgdate, imgtime1, product = f.split('_')
            imgtime2, scene, product, level, fileext = product.split('.')
            scene_id = '_'.join([marshrut, part, scene])
            if loop.has_key(scene_id):
                loop[scene_id][product]=os.path.join(root, f)
            else:
                loop[scene_id]={product:os.path.join(root, f)}

        # Resurs-P
        if re.search(r'^rp.*.l2\.tif$', f.lower(), flags=0):
            product_path = root
            sat, orbit, part, satname, imgdate, imgtime1, product = f.split('_')
            imgtime2, scene, product, level, fileext = product.split('.')
            scene_id = '_'.join([orbit, part, scene])

            if loop.has_key(scene_id):
                loop[scene_id][product]=os.path.join(root, f)
            else:
                loop[scene_id]={product:os.path.join(root, f)}

    # scroll(loop, header = 'Files:')
    # print(len(loop))

    i=1
    for item, v in loop.items():

        if v.has_key('PAN') and v.has_key('MS'):

            filename = os.path.basename(v['MS']).replace('.MS', '.PMS')
            psh = os.path.join(output_folder, filename)

            if filter_names is not None:
                stop = True
                for name in filter_names:
                    if name in filename:
                        filter_names.pop(filter_names.index(name))
                        stop = False
                        break
                if stop:
                    print('%i File excluded: %s' % (i, psh))
                    i += 1
                    continue

            if os.path.exists(psh):
                print('%i File already exists: %s' % (i, psh))
                i += 1
                continue
            else:
                print(item, v.keys(), u'%s from %s' % (i, len(loop.keys())))

            # print('Starting %s' % psh)

            t = 0
            while t < trynum:
                try:
                    if use_deflate:
                        tpath = tempname('tif')
                        image_psh(v['MS'], v['PAN'], tpath, bands, bands_ref, enhanced)
                        copydeflate(tpath, psh, bigtiff = True, tiled = True)
                        os.remove(tpath)
                    else:
                        image_psh(v['MS'], v['PAN'], psh, bands, bands_ref, enhanced)
                    success = True
                except:
                    print('Error processing %s, try again' % filename)
                    success = False
                    t += 1
                    time.sleep(30)


            if success:
                pass
            else:
                print('Error processing %s' % filename)

            i+=1

        else:
            print(item, v.keys(), u'%s from %s' % (i, len(loop.keys())))

    return filter_names

argv = sys.argv
if argv is None:
    sys.exit(1)

# scroll(filter_names)
# sys.exit(1)

suredir(output_folder)

filter_names = get_filter_names(filter_path, xlscolname=None, txtsep=';')

scroll(filter_names, header = 'Filter names for new tver:')

filter_names = pms_iter(data_source_folder,
             output_folder,
             bands = bands,
             bands_ref = bands_ref,
             enhanced = enhanced,
             use_deflate=use_deflate,
             filter_names=filter_names,
                trynum=20)

scroll(filter_names)
print(len(filter_names))

# sf=StereoFortuitous(data_source, output_file, relief_type, automode)
# if len(sf.all_metadata)==0:
#     print('Read data from SHP error.')
#     sf=None
#     sys.exit(1)
# else:
#     if output_file is None:sf.BatchModePairsAnalysis(False, False, True)
#     else:
#         output_file_type=os.path.basename(output_file.lower()).split('.')[1]
#         sf.BatchModePairsAnalysis(output_file_type=='xls', output_file_type=='txt', view_results)
