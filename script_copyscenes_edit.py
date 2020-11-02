# -*- coding: utf-8 -*-

from image_processor import *
from shutil import copyfile
from PIL import Image
import subprocess

# Пути к сценам
input_list = [
    # r'e:\data\kanopus_new\tver',
    r'g:\102_2020_126',
    # r'd:\digital_earth\2018_SNT\S2A_MSIL1C_20180525T084601_N0206_R107_T37VCC_20180525T110427.SAFE',
]


# Путь для сохранения копированных сцен
output_path = r'f:\examples'

# Путь к Экселевской таблице со статистикой копированных файлов
path2xls = r'E:\test\Tver_new.xls'
# path2xls = tempname('xls')

# Пути к векторным файлам ключевых участков
vector_cover_path_list = [
    # r'file:///C:/Users/admin/Desktop/point.shp',
]

print(u'Исходные данные загружены')

proc = process(output_path=output_path).input(input_list)

print(u'Обнаружено сцен: %i' % len(proc))

''' FILTER SCENES '''

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

print(u'Отфильтровано сцен по атрибутам: %i, проводится фильтрация по охвату' % len(proc))
# proc.get_vector_cover(r'resursp_filtered_cover.json') # Сохранить векторную маску

''' MANUAL FILTER BY QUICKLOOKS '''

# Returns a matrix of intersections between features in a list of shapefiles and image processor
def layers_intersection_array(shapes_list, proc):
    export_array = None
    for shp1 in shapes_list:
        result_array = None
        for ascene in proc.scenes:
            # print(os.path.basename(ascene.datamask()))
            if result_array is None:
                result_array = geodata.intersect_array(shp1, ascene.datamask())
                # print(np.unique(result_array, return_counts=True))
            else:
                new_array = geodata.intersect_array(shp1, ascene.datamask())
                # print(np.unique(new_array, return_counts=True))
                if new_array is not None:
                    # print(os.path.basename(ascene.datamask()))
                    result_array = np.hstack([result_array, new_array])
        if export_array is None:
            export_array = result_array
        else:
            if result_array is not None:
                export_array = np.vstack([export_array, result_array])
    return export_array

final_list = []
# qual_dict = {}
error_list = []

if len(vector_cover_path_list) > 0:
	intersection_array = layers_intersection_array(vector_cover_path_list, proc)
else:
	intersection_array = np.ones((1, len(proc.scenes))).astype(bool)

# print(intersection_array.shape)

scene_ids = np.array(proc.get_ids())

finish = False

while True:
	print(u'Провести визуальную проверку снимков (1) или нет (0)?')
	checkscenes = input(' >>> ')
	if checkscenes in (1,0):
		finish = bool(1-checkscenes)
        if finish:
            final_list = proc.get_ids()
        break

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
                    print(u'Введите 1 если качество сцены удовлетворительно или 0 если нет: ')
                    qualtest = input(' >>> ')

                    if qualtest == 1:
                        final_list.append(id)
                        approved = True
                        print(u'Сцена добавлена в список на копирование: {}'.format(id))
                        break

                    elif qualtest == 0:
                        print (u'Сцена помечена как неудовлетворительная: {}'.format(id))
                        approved = True

                    else:
                        raise Exception

                # p.kill()

            except:

                try:
                    print(u'Ошибка при оценке снимка, введите 101 чтобы пропустить сцену или 909 чтобы прервать операцию: ')
                    qualtest = input(' >>> ')
                    if qualtest == 101:
                        error_list.append(i)
                        approved = True
                        print(u'Сцена пропущена: {}'.format(id))
                        break

                    if qualtest == 909:
                        finish = True
                        print(u'Операция прервана пользователем')
                        break

                except:
                    # print(u'Неизвестная ошибка')
                    # break
                    pass

    else:
        print(u'Сцена за пределами области интереса: {}'.format(ascene.meta.id))

scroll(final_list, header=u'Список сцен для копирования:')

report_dict = OrderedDict()
for id in final_list:
    ascene = proc.get_scene(id)
    report_dict[id] = {
            'fullpath': ascene.fullpath,
            'date': ascene.meta.name('[date]'),
            'filepath': ascene.get_band_path('red')[0],
            'datamask': ascene.datamask(),
            'quicklook': ascene.quicklook(),
            # 'clouds': infullcloud(id),
        }
dict_to_xls(path2xls, report_dict)

''' ESTIMATE FILE SIZE '''

byte_size = 0
for id in final_list:
    path = proc.get_scene(id).path
    if os.path.exists(path):
        byte_size += count_dirsize(path)

while True:
	print(u'Всего отобрано {} сцен общим объёмом {}, выполнить копирование в {} (1) или отменить копирование (0)'.format(len(final_list), str_size(byte_size), output_path))
	copyfiles = input(' >>> ')
	if copyfiles in (1,0):
		break

if copyfiles:

    for id in final_list:
        ascene = proc.get_scene(id)
        scene_path = ascene.path
        scene_folder = os.path.basename(scene_path)
        scene_folder_path = fullpath(output_path, scene_folder)
        if not os.path.exists(scene_folder_path):
            os.makedirs(scene_folder_path)
        for filename in os.listdir(scene_path):
            copyfile(fullpath(scene_path, filename), fullpath(scene_folder_path, filename))
        print(u'Сцена сохранена {}'.format(id))