# -*- coding: utf-8 -*-

from image_processor import *

path = r'd:\rks\minprod\planet_new'
# print(path)
output_path = r'c:\sadkov\minprod'
shp_name = r'minprod_planet_cover.shp'
report_name = r'minprod_planet_new_composite.xls'
dates_list = [
    # '2019-05-20',
    '2019-06-23',
    '2019-06-25',
    '2019-07-23',
    # '2019-08-24',
    # '2019-08-30',
    '2019-08-29',
    '2019-09-10',
]

proc = process(output_path=output_path)
proc.input(path)
# scroll(proc.scenes)

def make_composites_from_list(ascene, complist, folder, name_template = '[id]_[comp].tif', compress = None, overwrite = True):
    for comp_id in complist:
        filename = ascene.meta.name(name_template.replace('[comp]', str(comp_id)))
        full = fullpath(folder, filename)
        res = ascene.default_composite(comp_id, full, compress = compress, overwrite = overwrite)
        if res == 1:
            # print(ascene.meta.name('[date]'))
            newpath = r'd:\rks\minprod\planet\{}\{}'.format(ascene.meta.name('[date]'), ascene.meta.filepaths.get('Analytic'))
            print(newpath)
            if os.path.exists(newpath):
                # print('Trying another path: {}'.format(newpath))
                res = geodata.raster2raster([(newpath, 3), (newpath, 2), (newpath, 1)],
                                      full,
                                      # path2target=path2target,
                                      # exclude_nodata=exclude_nodata,
                                      # enforce_nodata=enforce_nodata,
                                      compress=compress,
                                      overwrite=overwrite)
                # res = ascene.composite(comp_id, full, compress = compress, overwrite = overwrite)
            # else:
                # print('File not found: {}'.format(newpath))
    return res

report = OrderedDict()

for ascene in proc.scenes:
    marker = (ascene.meta.name('[date]'), i)
    print(ascene.meta.lvl)
    if scene_date in dates_list:
        folder = r'C:\sadkov\minprod\planet\composites\{}'.format(scene_date)
        if not os.path.exists(folder):
            os.makedirs(folder)
        res = make_composites_from_list(ascene, ['RGB'], folder, name_template='minprod_[id]_[comp].tif', compress='LERC_DEFLATE', overwrite=False)
        scene_report = OrderedDict()
        # scene_report['id'] = ascene.meta.id
        scene_report['result'] = res
        report['id'] = scene_report

try:
    dict_to_xls(fullpath(proc.output_path, report_name), report)
except:
    scroll(report)
    pass