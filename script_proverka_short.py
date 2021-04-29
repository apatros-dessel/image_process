from tools import *
from PIL import Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path', help='Путь для поиска исходных данных')
parser.add_argument('-x', default=None, dest='xls_name', help='Название таблицы Excel')
parser.add_argument('-t', default=None, dest='type', help='Тип данных (KAN или RSP)')
parser.add_argument('-b', default='MS', dest='band_type', help='Тип данных (MS, PAN или PMS)')
parser.add_argument('-o', default='report.xls', dest='xls_out', help='Название выходного файла')
parser.add_argument('--pathmark', default=None, dest='pathmark', help='Маркер пути к файлу')
args = parser.parse_args()
type_tmpt = {'KAN':'KV','RSP':'RP'}.get(args.type.upper())
xls_name = args.xls_name
xls_out = args.xls_out
band_type = args.band_type
pathmark = args.pathmark
if pathmark is not None:
    pathmark = obj2list(pathmark.split(','))
path = args.path

def CheckImage(img_path):
    approved = False
    while not approved:
        try:
            with Image.open(img_path) as quicklook:
                quicklook.show()
                print(u'Введите числовой индекс файла {}'.format(os.path.basename(img_path)))
                qualtest = int(input(' >>> '))
                if qualtest in (909, 101):
                    print('Недопустимое значение - %i' % qualtest)
                    continue
                return qualtest
        except:
            try:
                print(
                    u'Ошибка при оценке снимка 101 чтобы пропустить сцену или 909 чтобы прервать операцию: ')
                qualtest = int(input(' >>> '))
                if qualtest == 101:
                    print(u'Файл пропущен: {}'.format(os.path.basename(img_path)))
                    return None
                if qualtest == 909:
                    print(u'Операция прервана пользователем')
                    return 909
            except:
                pass

def CheckPathmark(marks, path):
    if marks is None:
        return True
    else:
        for mark in obj2list(marks):
            if mark in path:
                return True
    return False

files = folder_paths(path,1,'jpg')

end = OrderedDict()
if xls_name:
    end = xls_to_dict(xls_name)
    if end is None:
        end = OrderedDict()

for i, file in enumerate(files):
    if (i+1)%100==0:
        if len(end)>0:
            dict_to_xls(fullpath(path, xls_out), end)
    name = os.path.basename(file)
    # print(file, pathmark, band_type)
    if not CheckPathmark(pathmark, file):
        continue
    if not band_type in name:
        continue
    if type_tmpt:
        if re.search(type_tmpt,name) is None:
            continue
    result = CheckImage(file)
    if result==909:
        break
    report = OrderedDict()
    report['id'] = name
    report['mark'] = result
    end[file] = report

saving = Confirmation('Проверка окончена, сохранить результаты (y/n)?')
if saving:
    dict_to_xls(fullpath(path, xls_out), end)
