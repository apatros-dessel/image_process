# -*- coding: utf-8 -*-

import os
import re
import shutil

template = r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PMS.L\d.tif'
r'KV1_37536_29328_01_KANOPUS_20190428_091817_091918.SCN4.PMS.L2.tif'

input_dir = r''
output_dir = None

def kanopus_index(filename):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = undersplit = filename.split('_')
    num2, scn, type, lvl, ext = dotsplit = ending.split('.')
    if type!='PMS':
        return None
    scn_num = scn.rplace('SCN', '')
    indexname = 'IM4-{satid}-{date}-{loc1}{loc2}{scn_num}-{lvl}.{ext}'.format(satid, date, loc1, loc2, scn_num, lvl, ext)
    return indexname

while not os.path.exists(input_dir):
    try:
        print(u'Введите путь к файлам паншарпов')
        input_dir = str(input('  >>>  '))
    except:
        pass

if (output_dir is None) or output_dir==input_dir:
    copy = False
else:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    copy = True


listdir = os.listdir(input_dir)

for filename in listdir:
    if re.search(template, filename) is not None:
        try:
            new_name = kanopus_index(filename)
        except:
            new_name = None
        if new_name is not None:
            if copy:
                shutil.copyfile(os.path.join(input_dir, filename), os.path.join(output_dir, filename))
                print('File written: {}'.format(new_name))
            else:
                os.rename(os.path.join(input_dir, filename), os.path.join(input_dir, filename))