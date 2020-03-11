# -*- coding: utf-8 -*-

import os
import re
import shutil

template = r'KV\S_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PMS.L\d.tif'
# r'KV1_37536_29328_01_KANOPUS_20190428_091817_091918.SCN4.PMS.L2.tif'

# Папка с исходными снимками Канопус
input_dir = r'd:\digital_earth\kanopus_new\krym\KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.PMS_a83ad8ca9d24564842d1d060588fa062fe97a0aa'

# Папка с переименованными снимками Канопус
output_dir = r'd:\digital_earth\kanopus_new\krym\KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.PMS_a83ad8ca9d24564842d1d060588fa062fe97a0aa\new'

def kanopus_index(filename):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = undersplit = filename.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    type = dotsplit[2]
    lvl = dotsplit[3]
    ext = dotsplit[-1]
    scn_num = scn.replace('SCN', '')
    indexname = 'IM4-{}-{}-{}{}{}-{}.{}'.format(satid, date, loc1, loc2, scn_num, lvl, ext)
    return indexname

if (output_dir is None) or output_dir==input_dir:
    copy = False
else:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    copy = True

listdir = os.listdir(input_dir)

for filename in listdir:

    if os.path.isdir(filename):
        continue

    if re.search(template, filename) is not None:

        new_name = kanopus_index(filename)

        try:
            new_name = kanopus_index(filename)
        except:
            print(u'Ошибка переименования: {}'.format(filename))
            new_name = None

        if new_name is not None:
            if copy:
                shutil.copyfile(os.path.join(input_dir, filename), os.path.join(output_dir, new_name))
                print(u'Файл скопирован: {}'.format(new_name))
            else:
                shutil.move(os.path.join(input_dir, filename), os.path.join(output_dir, new_name))
                print(u'Файл переименован: {}'.format(new_name))

    else:
        # print(u'Файл пропущен: {}'.format(filename))
        pass