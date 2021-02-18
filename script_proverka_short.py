from tools import *
from PIL import Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path', help='Путь для поиска исходных данных')
parser.add_argument('-x', default=None, dest='xls_name', help='Название таблицы Excel')
parser.add_argument('-t', default=None, dest='type', help='Тип данных (KAN или RSP)')
args = parser.parse_args()
type_tmpt = {'KAN':'KV','RSP':'RP'}.get(args.type.upper())
xls_name = args.xls_name
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

files = folder_paths(path,1,'jpg')

if xls_name:
    xls_dict = xls_to_dict(xls_name)
else:
    xls_dict = None
end = OrderedDict()

for file in files:
    name = os.path.basename(file)
    if type_tmpt:
        if re.search(type_tmpt,name) is None:
            continue
    if xls_dict:
        if not (name in xls_dict):
            continue
    result = CheckImage(file)
    if result==909:
        break
    report = OrderedDict()
    report['id'] = name
    report['mark'] = result
    end[file] = report

dict_to_xls(fullpath(path, 'report.xls'), end)
