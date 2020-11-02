# -*- coding: utf-8 -*-

from image_processor import process
from geodata import *
import sys

din = r'e:\tos3'
dout = r'e:\rks\s3'

tmpt_snt = '^S2[AB]_MSI.+\d$'
tmpt_pln = '.*AnalyticMS(_SR)?$'
tmpt_pln_neuro = 'IM4-PLN.*'

source = r'e:\rks\source'
tcover = r'e:\rks\s3\cover.json'
process().input(source).GetCoverJSON(tcover)

def cleansplit(str_, sep, join=''):
    ids = str_.split(sep)
    for i, id in enumerate(ids):
        if i:
            ids[i] = join+id
    return ids

def get_export_list(din):
    export = OrderedDict()
    for path in folder_paths(din,1,'tif'):
        f, n, e = split3(path)
        if re.search(tmpt_snt, n):
            ids = cleansplit(n, '_S2', 'S2')
            for i, id in enumerate(ids):
                export[id] = (path, (4*i+3, 4*i+2, 4*i+1, 4*i+4))
        elif re.search(tmpt_pln, n):
            export[n] = (path, (3, 2, 1, 4))
        elif re.search(tmpt_pln_neuro, n):
            mark, sat, date, loc, lvl = n.split('-')
            id = '%s_%s_%s_%s_AnalyticMS' % (date, loc[1:], sat[3:], lvl[1:])
            export[id] = (path, (1, 2, 3, 4))

    return export

export_dict = get_export_list(din)

scroll(export_dict.keys(), header='%i objects found:' % len(export_dict))

for id in export_dict:

    if (id+'_SR') in export_dict:
        print('Abort operation -- SR scene found: %s' % id)
        continue
    elif id.endswith('_SR'):
        id = id[:-3]

    path_in, bands_list = export_dict[id]
    img_path = fullpath(dout, id)
    suredir(img_path)
    path_out = fullpath(img_path, id, 'tif')
    res = SaveRasterBands(path_in, bands_list, path_out, options={'compress':'DEFLATE','dt':6}, overwrite=False)
    if res==0:
        print('Scene written: %s'% id)
    else:
        print('Error writing scene: %s' % id)

    json_out = fullpath(img_path, id, 'json')
    tmetapath = filter_dataset_by_col(tcover, 'id', [id, id.replace('_MSIL2A_', '_MSIL1C_')], path_out = json_out)
    json_fix_datetime(json_out)
    print('Metadata written: %s' % id)
