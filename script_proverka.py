# -*- coding: utf-8 -*-

dir_in = os.getcwd()
try:
    os.chdir(r'\\172.21.195.215\thematic\exchange\Sadkov_SA\code\image_process')
except:
    print('Cannot chdir')
    pass
try:
    from image_processor import *
except:
    print('Cannot import image_processor')
    sys.exit(1)
from PIL import Image
import argparse

parser = argparse.ArgumentParser(description='Given 2 geotiff images finds transformation between')
parser.add_argument('-d', default=None, dest='dir_in', help='Input folder')
parser.add_argument('-o', default=None, dest='dir_out', help='Output folder')
parser.add_argument('-x', default='report.xls', dest='xls', help='Excel report table')
parser.add_argument('-v', default=None, dest='v_cover', help='Vector cover path')
args = parser.parse_args()
if args.dir_in is not None:
    dir_in = args.dir_in
if args.dir_out is None:
    dir_out = dir_in
else:
    dir_out = args.dir_out
xls = fullpath(dir_out, args.xls)
v_cover = args.v_cover

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

print(u'Фильтрация сцен отключена')

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

marks_dict = OrderedDict()
qual_dict = {}
error_list = []
code_list = []

if v_cover:
	intersection_array = layers_intersection_array([v_cover], proc)
else:
	intersection_array = np.ones((1, len(proc.scenes))).astype(bool)

scene_ids = np.array(proc.get_ids())

finish = False

for i, ascene in enumerate(proc.scenes):

    if finish:
        break

    if np.sum(intersection_array[:, i]) > 0:

        id = ascene.meta.id

        approved = False

        while not approved:

            try:

                # p = subprocess.Popen(['display', ascene.quicklook()])

                with Image.open(ascene.quicklook()) as quicklook:
                    quicklook.show()
                    print(u'Введите числовой индекс сцены {}'.format(id))
                    qualtest = input(' >>> ')

                    if qualtest not in code_list:
                        code_list.append(qualtest)

                    marks_dict[id] = str(qualtest)
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
                    print(u'Ошибка при оценке снимка, введите 101 чтобы пропустить сцену или 909 чтобы прервать операцию: ')
                    qualtest = input(' >>> ')

                    if qualtest == 101:
                        error_list.append(id)
                        approved = True
                        marks_dict[id] = 'None'
                        print(u'Сцена пропущена: {}'.format(id))
                        break

                    if qualtest == 909:
                        finish = True
                        print(u'Операция прервана пользователем')
                        break

                except:
                    pass

    else:
        print(u'Сцена за пределами области интереса: {}'.format(ascene.meta.id))

report_dict = OrderedDict()
for id in marks_dict.keys():
    ascene = proc.get_scene(id)
    line = OrderedDict()
    line['path'] = ascene.path
    line['date'] = ascene.meta.name('[date]')
    line['mark'] = marks_dict[id]
    report_dict[id] = line
dict_to_xls(xls, report_dict)

scroll(code_list, header=u'Использованные коды оценок')

input(u'  Нажмите Enter для выхода  ')
