# -*- coding: utf-8 -*-

import os, sys, argparse
try:
    from image_processor import *
except:
    print('Cannot import image_processor')
    sys.exit(1)
from PIL import Image

parser = argparse.ArgumentParser(description='Given 2 geotiff images finds transformation between')
parser.add_argument('-d', default=None, dest='dir_in',  help='Input folder')
parser.add_argument('-o', default=None, dest='dir_out', help='Output folder')
parser.add_argument('-x', default='report.xls', dest='xls', help='Excel report table')
parser.add_argument('-v', default=None, dest='v_cover', help='Vector cover path')
parser.add_argument('-t', default=None, dest='type', help='Scene type')
args = parser.parse_args()
if args.dir_in is None:
    dir_in = 'None'
    while True:
        print(u'Введите путь к исходным данным:')
        dir_in = str(input(' >>> '))
        if os.path.exists(dir_in):
            break
        else:
            print('Путь не найден: %s' % dir_in)
else:
    dir_in = args.dir_in
if args.dir_out is None:
    dir_out = dir_in
else:
    dir_out = args.dir_out
xls = fullpath(dir_out, args.xls)
v_cover = args.v_cover
type = None
if args.type is not None:
    if args.type.upper() in ['PAN', 'MS', 'PMS']:
        type = args.type.upper()

'''
# Пути к сценам
input_list = [
    r'G:\102_2020_116',
    # r'd:\digital_earth\2018_SNT\S2A_MSIL1C_20180525T084601_N0206_R107_T37VCC_20180525T110427.SAFE',
]

# Путь для сохранения копированных сцен
output_path = r'E:\script export'

# Путь к Экселевской таблице со статистикой копированных файлов
path2xls = r'E:\script export\krym.xls'

# Пути к векторным файлам ключевых участков
vector_cover_path_list = [
    # r'E:\script export/maska2.shp',
]
'''

print(u'Исходные данные загружены')

proc = process().input(dir_in, skip_duplicates=False)

if v_cover is None:
    v_cover = tempname('json')
    del_v_cover = True
    proc.GetCoverJSON(v_cover)
else:
    del_v_cover = False

print(u'Обнаружено сцен: %i' % len(proc))

''' FILTER SCENES '''
'''
ids_list = proc.get_ids()
for id in ids_list:
    ascene = proc.get_scene(id)

    # В Канопус и Ресурс-П удалить все сцены кроме паншарпов
    if ascene.imsys in ['KAN', 'RSP']:
        if not '.PMS.' in id:
            proc.del_scene(id)
            continue

    # Удалить сцены зимних месяцев
    month = int(ascene.meta.datetime.month)
    if (month>10) or (month<4):
        proc.del_scene(id)

print(u'Отфильтровано сцен для ручной обработки: %i' % len(proc))
# proc.get_vector_cover(r'resursp_filtered_cover.json') # Сохранить векторную маску
'''


''' MANUAL FILTER BY QUICKLOOKS '''

# Returns a matrix of intersections between features in a list of shapefiles and image processor
def layers_intersection_array(shapes_list, proc):
    export_array = None
    for shp1 in shapes_list:
        result_array = None
        for ascene in proc.scenes:
            if result_array is None:
                result_array = geodata.intersect_array(shp1, ascene.datamask())
            else:
                new_array = geodata.intersect_array(shp1, ascene.datamask())
                if new_array is not None:
                    result_array = np.hstack([result_array, new_array])
        if export_array is None:
            export_array = result_array
        else:
            if result_array is not None:
                export_array = np.vstack([export_array, result_array])
    return export_array

def input_parameters(dir_out, xls, type):
    print('Введите новый параметр проверки, с указанием индекса:\n  -o <путь к конечному файлу>\n  -x <название файла отчёта (xls)>\n  -t <тип данных (PAN, MS, PMS)>')
    params = input('  >>>  ').strip()
    if re.search('^-[otx] ', params):
        type = params[1]
        val = params[3:]
        if type=='o':
            dir_out = val
        elif type=='x':
            xls = val
            xls = fullpath(dir_out, xls)
        elif type=='t':
            type = val.upper()
        else:
            print('Unreckognized type: %s' % type)
    else:
        print('Wrong parameter string: %s' % params)
    return dir_out, xls, type

marks_dict = OrderedDict()
qual_dict = {}
error_list = []
code_list = []
'''
if v_cover:
	intersection_array = layers_intersection_array([v_cover], proc)
else:
	intersection_array = np.ones((1, len(proc.scenes))).astype(bool)
'''
scene_ids = np.array(proc.get_ids())

finish = False

for i, ascene in enumerate(proc.scenes):

    if finish:
        break

    if ascene:

        id = ascene.meta.id
        path = ascene.fullpath

        approved = False

        while not approved:

            try:
                if type:
                    if ascene.meta.type != type:
                        approved = True
                        break
                # p = subprocess.Popen(['display', ascene.quicklook()])

                with Image.open(ascene.quicklook()) as quicklook:
                    quicklook.show()
                    print(u'Введите числовой индекс сцены {}'.format(id))
                    qualtest = int(input(' >>> '))

                    if qualtest not in code_list:
                        code_list.append(qualtest)

                    marks_dict[path] = str(qualtest)
                    break

                    # if qualtest == 1:
                        # final_list.append(id)
                        # approved = True
                        # print(u'Сцена добавлена в список на копирование: {}'.format(id))
                        # break

                    # elif qualtest == 0:
                        # print (u'Сцена помечена как неудовлетворительная: {}'.format(id))
                        # approved = True

                    # else:
                        # raise Exception

                # p.kill()

            except:

                try:
                    print(u'Ошибка при оценке снимка, введите 100 чтобы изменить параметры, 101 чтобы пропустить сцену или 909 чтобы прервать операцию: ')
                    qualtest = int(input(' >>> '))

                    if qualtest==100:
                        dir_out, xls, type = input_parameters(dir_out, xls, type)

                    if qualtest==101:
                        error_list.append(id)
                        approved = True
                        marks_dict[path] = 'None'
                        print(u'Сцена пропущена: {}'.format(id))
                        break

                    if qualtest==909:
                        finish = True
                        print(u'Операция прервана пользователем')
                        break

                except:
                    pass

    else:
        print(u'Сцена за пределами области интереса: {}'.format(ascene.meta.id))

scroll(code_list, header=u'Использованные коды оценок')
saving = Confirmation('Проверка окончена, сохранить результаты (y/n)?')
if saving:
    report_dict = OrderedDict()
    for path in marks_dict.keys():
        proc = process().input(path)
        if proc:
            ascene = proc.scenes[0]
            id = ascene.meta.id
            line = OrderedDict()
            line['id'] = id
            line['date'] = ascene.meta.name('[date]')
            line['mark'] = marks_dict[path]
            report_dict[path] = line
        else:
            print('ERROR UPDATING PATH: %s' % path)
    suredir(dir_out, 0)
    dict_to_xls(xls, report_dict)
    print('Сохранено %i результатов' % len(report_dict))

input(u'\n  Нажмите Enter для выхода  ')

if del_v_cover:
    os.remove(v_cover)
