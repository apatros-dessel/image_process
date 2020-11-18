# -*- coding: utf-8 -*-

from image_processor import *

# input_path = r'c:\sadkov\toropez\planet\20190516'
input_path_list = [
                    # r'F:\rks\toropez\planet',
                    # r'F:\rks\tver',
                    r'f:\rks\forest',
                  ]
output_path = r'f:\rks\digital_earth\planet'

path2composite = r'{}\composite'.format(output_path)
path2rgb = r'{}\rgb'.format(output_path)

proc = process(output_path=output_path)
# proc.input(input_path)
for in_path in input_path_list:
    proc.input(in_path, imsys_list=['PLN'])

shp_name = r'planet_cover_forest.json'
report_name = r'planet_cover_forest.xls'

path2vector_list = []

t = datetime.now()
report = OrderedDict()
for ascene in proc.scenes:
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

# geodata.unite_vector(path2vector_list, fullpath(proc.output_path, shp_name))

geodata.JoinShapesByAttributes(path2vector_list, fullpath(proc.output_path, shp_name), ['id'], geom_rule=1, attr_rule=0)