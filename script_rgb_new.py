# -*- coding: utf-8 -*-

from image_processor import *

sat_rgb = {
    'PL': [3,2,1],
    'KV': [1,2,3],
    'RP': [1,2,3],
}

path = [
    # r'd:\digital_earth\resurs-p_new\krym\2074509_220120_Krym',
    r'd:\digital_earth\resurs-p_new\krym',
    ]

obj_of_interest = r'D:\digital_earth\data_2_razmetka\other\20200228\TBO_krym_point.shp'
check_obj = os.path.exists(obj_of_interest)

folder = r'e:\kanopus_new'



if not os.path.exists(folder):
    os.makedirs(folder)

proc = process()
proc.input(path)

raster_path_dict = {}
print('Start processing %i scenes' % len(proc))

report = OrderedDict()

''' GROUP SCENES BY SATELLITE AND DATE '''
for ascene in proc.scenes:

    if ascene.imsys in ['LST', 'SNT']:
        # The script doesnt work for these image systems yet
        continue

    if ascene.imsys in ['KAN', 'RSP']:
        if not '.PMS.' in ascene.meta.id:
            continue

    if check_obj:
        if not geodata.ShapesIntersect(obj_of_interest, ascene.datamask()):
            # print('Not intersected: %s' % ascene.meta.id)
            continue

    strip_id = ascene.meta.name('[sat]-[date]')
    raster_path = ascene.get_band_path('red')[0]

    sat, date = strip_id.split('-')
    report[ascene.meta.id] = {'stripid': strip_id, 'sat': sat, 'date': date}

    if strip_id in raster_path_dict:
        raster_path_dict[strip_id].append(raster_path)
    else:
        raster_path_dict[strip_id] = [raster_path]

# scroll(raster_path_dict, header='Raster paths:')

sum = 0
for key in raster_path_dict:
    sum += len(raster_path_dict[key])
    scroll(raster_path_dict[key], header='Raster path for: %s' % key)
print(len(raster_path_dict), sum)

dict_to_xls(r'e:\test\resurs-p_ofinterest.xls', report)

raise Exception

errors_list = []

# border_list = geodata.GetRasterPercentiles(raster_path_dict[raster_path_dict.keys()[0]], min_percent = 0.01, max_percent = 0.995, band_num_list = [3,2,1], nodata = 0)

# print(border_list)

''' MAKING RGB FOR EACH GROUP '''
for strip_id in raster_path_dict:

    raster_path_list = raster_path_dict[strip_id]
    # band_hist_dict = [{},{},{}]
    # borders_list = []

    sat = strip_id[:2]

    path2export_list = []

    for path2raster in raster_path_list:
        path2export = r'{}\{}\{}\{}'.format(folder, sat, strip_id[-8:], os.path.split(path2raster)[1])
        if os.path.exists(path2export):
            print('File already exists: {}'.format(path2export))
        else:
            path2export_list.append((path2raster, path2export))

    if len(path2export_list) == 0:
        continue

    ''' MAKE HYSTOGRAMS FOR EACH GROUP '''
    borders_list = geodata.GetRasterPercentiles(raster_path_list, min_percent = 0.01, max_percent = 0.995, band_num_list = [3,2,1], nodata = 0)

    print('Start processing %i scenes' % len(path2export_list))

    ''' SAVING EVERY SCENE WITH THIS HYSTOGRAM '''
    for path2raster, path2export in path2export_list:
        if not os.path.exists(os.path.split(path2export)[0]):
            os.makedirs(os.path.split(path2export)[0])
        # path2export = r'{}\{}'.format(folder, os.path.split(path2raster)[1])
        # res = geodata.RasterToImage3(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], reprojectEPSG=3857, compress='LZW', overwrite=False, alpha=False)

        try:
            # res = geodata.RasterToImage2(path2raster, path2export, method=3, band_limits=borders_list, gamma=0.85, exclude_nodata=True, enforce_nodata=0, band_order=[3, 2, 1], compress='LZW', overwrite=False, alpha=False)
            res = geodata.RasterToImage3(path2raster,
                                         path2export,
                                         method=3,
                                         band_limits=borders_list,
                                         gamma=0.85,
                                         exclude_nodata=True,
                                         enforce_nodata=0,
                                         band_order=globals()['sat_rgb'].get(sat),
                                         reprojectEPSG = 3857,
                                         compress='LZW',
                                         overwrite=False,
                                         alpha=False)
        except:
            res = 1
        if res == 0:
            print('File written: {}'.format(path2export))
        else:
            print('Failed to write file: {}'.format(path2export))
            errors_list.append(path2export)

if len(errors_list) > 0:
    scroll(errors_list, header='Errors while procesing files:')

