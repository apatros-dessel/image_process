# -*- coding: utf-8 -*-

from image_processor import *

path = r'd:\rks\tver'
output_path = r'c:\sadkov\planet_tverskaya\borders\fall'
shp_name = r'tver_planet_cover_fall.shp'
report_name = r'tver_planet_cover_fall.xls'

proc = process(output_path=output_path)
proc.input(path)

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

geodata.unite_vector(path2vector_list, fullpath(proc.output_path, shp_name))