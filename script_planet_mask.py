# -*- coding: utf-8 -*-

from image_processor import *

# input_path = r'c:\sadkov\toropez\planet\20190516'
input_path_list = [r'c:\sadkov\toropez\planet',
                   r'd:\rks\toropez\planet']
output_path = r'c:\sadkov\toropez\image_test\full'

path2composite = r'{}\composite'.format(output_path)
path2rgb = r'{}\rgb'.format(output_path)

proc = process(output_path=output_path)
# proc.input(input_path)
for in_path in input_path_list:
    proc.input(in_path, imsys_list=['PLN'])

shp_name = r'planet_cover.shp'
report_name = r'planet_cover.xls'

'''
def date_covers(proc):
    dates_list = proc.get_dates()
    scene_dict = OrderedDict()

    for date in dates_list:
        path2vector_list = []
        for ascene in proc.scenes:
            if date == ascene.meta.datetime.date():
                path2vector_list.append(fullpath(ascene.path, ascene.meta.datamask))
        scene_dict[date] = path2vector_list
        shp_name = 'minprod_planet_cover_{}.shp'.format(date)
        geodata.unite_vector(path2vector_list, fullpath(proc.output_path, shp_name))

    try:
        dict_to_xls(fullpath(proc.output_path, report_name), scene_dict)
    except:
        # scroll(scene_dict)
        pass

    return None
'''

# date_covers(proc)

path2vector_list = []

t = datetime.now()
report = OrderedDict()
for ascene in proc.scenes:
    print(ascene.meta.datamask)
    path2vector_list.append(fullpath(ascene.path, ascene.meta.datamask))
    # path2vector_list.append(ascene.meta.datamask)
    rep_row = OrderedDict()
    rep_row['datamask'] = path2vector_list[-1]

    report[ascene.meta.id] = rep_row

print('Total time = {}'.format(datetime.now()-t))

try:
    dict_to_xls(fullpath(proc.output_path, report_name), report)
except:
    print('Unable to export data as xls')
    scroll(report)

scroll(path2vector_list)

geodata.unite_vector(path2vector_list, fullpath(proc.output_path, shp_name))