# from tools import *
import sys, os, shutil, re, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', default=None, dest='folders', help='Папки с исходными данными, через запятую')
parser.add_argument('-c', default=None, dest='copyfolder', help='Папка для копирования')
parser.add_argument('-i', default=None, dest='indices', help='Индексы файлов для копирования, через запятую')
parser.add_argument('-l', default=None, dest='txt_ids', help='Файл со списком индексов для копирования (должны быть записаны построчно, в формате txt)')
parser.add_argument('--checksum', default=True, dest='checksum', help='Проверять контрольные суммы при совпадении файлов')
args = parser.parse_args()

def boolstr(val):
    if isinstance(val, str):
        if val.lower() in ['false', 'n', 'no', '0']:
            val = False
        else:
            val = True
    return val

def SeparateStrings(str_, separator = ',', as_folder = False):
    fin = []
    parts = str_.strip().split(separator)
    for part in parts:
        part = part.strip()
        if part == '':
            continue
        if as_folder:
            part = part.rstrip('\\') + '\\'
        fin.append(part)
    return fin

def FileIndexAsList(path, ext):
    files = []
    ext = '.' + ext.lstrip('.')
    for corner, _folders, _files in os.walk(path):
        for file in _files:
            if file.endswith(ext):
                files.append(corner + '\\' + file)
    return files

def FileIndex(path, ext):
    files = FileIndexAsList(path, ext)
    if files:
        with open(path + r'\tif_index.txt', 'w') as txt:
            txt.write('\n'.join(files))

def CheckSum(path):
    h = hashlib.sha1()
    with open(path, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()

class CheckSumError(Exception):

    def __init__(self, *args, **kwargs):
        pass

if args.folders is None:
    print('Введите исходные папки для копирования, через запятую: ')
    folders = SeparateStrings(input('  >>> '), as_folder = True)
else:
    folders = SeparateStrings(args.folders, as_folder = True)

# for c,fs,f_ in os.walk('y:\\'):
    # for f in fs:
        # folders.append(c + f)
    # break

if args.copyfolder is None:
    print('Введите путь к конечной папке для копирования (она должна существовать): ')
    folder_out = input('  >>> ').strip().rstrip('\\') + '\\'
else:
    folder_out = args.copyfolder.strip().rstrip('\\') + '\\'

txt_ids = None
if args.txt_ids is None:
    print('Укажите путь к списку файлов для копирования, если необходимо: ')
    ids_path = input('  >>> ').strip()
else:
    ids_path = args.txt_ids.strip()
if ids_path:
    txt_path = args.txt_ids
    if os.path.exists(txt_path):
        try:
            txt_ids = SeparateStrings(open(txt_path).read(), separator = '\n')
        except:
            print('Ошибка чтения файла: ' + txt_path)
            txt_ids = None

if args.indices is None:
    if txt_ids is None:
        print('Введите индексы файлов для копирования, через запятую:')
        ids = SeparateStrings(input('  >>> '))
    else:
        ids = txt_ids
else:
    ids = SeparateStrings(args.indices)
    if txt_ids is not None:
        ids.extend(txt_ids)

try:
    import hashlib
    checksum = boolstr(args.checksum)
except:
    input('Не удалось импортировать hashlib, контроль дубликатов отключён')
    checksum = False

done = []

for folder in folders:
    if folder.startswith('y:'):
        paths = FileIndexAsList(folder, 'tif')
    else:
        tif_index = folder + r'\tif_index.txt'
        if not os.path.exists(tif_index):
            FileIndex(folder, 'tif')
        if os.path.exists(tif_index):
            try:
                paths = open(tif_index).read().split('\n')
            except:
                print('\n  Ошибка чтения индекса: ' + tif_index)
                continue
        else:
            print('Список файлов не найден: %s' % tif_index)
            continue
    for path in paths:
        try:
            for id in ids:
                if re.search(id, path):
                    name = os.path.split(path)[1]
                    path_out = folder_out + '\\' + name
                    i = 0
                    path_out_ = path_out
                    while os.path.exists(path_out_):
                        i += 1
                        if checksum:
                            if CheckSum(path) == CheckSum(path_out_):
                                print('%s Обнаружен дубликат: %s' % (id, path))
                                done.append(id)
                                raise CheckSumError
                        path_out_ = path_out.replace('.tif', '_%i.tif' % i)
                    shutil.copyfile(path, path_out_)
                    print('%s Скопировано из: %s' % (id, path))
                    done.append(id)
        except CheckSumError:
            pass

print('')
for id in ids:
    if not id in done:
        print('Индекс не найден: ' + id)

input(' Копирование завершено, нажмите Enter для выхода')