import sys, os, shutil, argparse, hashlib
from progress.bar import IncrementalBar

parser = argparse.ArgumentParser()
parser.add_argument('folder_in', help='Папка с исходными данными')
parser.add_argument('folder_out', help='Папка для копирования')
parser.add_argument('--checksum', default=True, dest='checksum', help='Проверять контрольные суммы (по умолчанию - True)')
args = parser.parse_args()
folder_in = args.folder_in
folder_out = args.folder_out

def boolstr(val):
    if isinstance(val, str):
        if val.lower() in ['false', 'n', 'no', '0']:
            val = False
        else:
            val = True
    return val

checksum = boolstr(args.checksum)

def FoldersFiles(path):
    folders = [path]
    files = []
    for corner, _folders, _files in os.walk(path):
        for folder in _folders:
            folders.append(corner + '\\' + folder)
        for file in _files:
            files.append(corner + '\\' + file)
    return folders, files

def delete(path):
    if os.path.exists(path):
        try:
            os.remove(path)
        except:
            print('CANNOT DELETE: %s' % path)

def CheckSum(path):
    h = hashlib.sha1()
    with open(path, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()

def DownloadAndCheck(ifile, ofile, iter_lim = 10, checksum = True):
    iter = 0
    if checksum:
        check = CheckSum(ifile)
        while check != CheckSum(ofile):
            if iter > iter_lim:
                print(' ITERATION NUMBER EXEEDED: %s' % Name(ifile))
                return None
            delete(ofile)
            shutil.copyfile(ifile, ofile)
            iter += 1
    else:
        while os.path.getsize(ifile) != os.path.getsize(ofile):
            if iter > iter_lim:
                print(' ITERATION NUMBER EXEEDED: %s' % Name(ifile))
                return None
            delete(ofile)
            shutil.copyfile(ifile, ofile)
            iter += 1
    return os.path.getsize(ofile)

def str_size(byte_size):
    assert byte_size >= 0
    if byte_size < 1024:
        return u'{} байт'.format(round(byte_size, 2))
    elif byte_size < (1024**2):
        return u'{} Кб'.format(round(byte_size/1024, 2))
    elif byte_size < (1024**3):
        return u'{} Мб'.format(round(byte_size/(1024**2), 2))
    elif byte_size < (1024**4):
        return u'{} Гб'.format(round(byte_size/(1024**3), 2))
    elif byte_size < (1024**5):
        return u'{} Тб'.format(round(byte_size/(1024**4), 2))
    elif byte_size > (1024**6):
        print(u'Полученный размер больше 1 Пб, вероятно что-то пошло не так')
        return None

print('\nИдёт поиск файлов в %s' % folder_in)
input_folders, input_files = FoldersFiles(folder_in)
cut_len = len(folder_in)

print('\nОбнаружено %i файлов, начать копирование:\n из: \t%s\n в: \t%s\n%s ? (y/n)' % (len(input_files), folder_in, folder_out, [' без проверки контрольных сумм', ' с проверкой контрольных сумм'][checksum]) )

while True:
    i = 0
    try:
        if i >= 10: sys.exit()
        start = boolstr(input(' >>>'))
    except:
        i += 1
    else:
        # print('\n')
        break

if not start:
    sys.exit()

for ifolder in input_folders:
    if '.PMS' in ifolder:
        continue
    else:
        ofolder = r'%s\%s' % (folder_out, ifolder[cut_len:])
        if os.path.exists(ofolder):
            pass
        else:
            os.makedirs(ofolder)

copy_size = 0
exists_size = 0
miss_size = 0
error_size = 0
bar = IncrementalBar('Идёт загрузка: ', max = len(input_files))

for ifile in input_files:
    ofile = r'%s\%s' % (folder_out, ifile[cut_len:])
    ofolder, oname = os.path.split(ofile)
    if '.PMS' in ofile:
        miss_size += os.path.getsize(ifile)
    elif os.path.exists(ofile):
        size = DownloadAndCheck(ifile, ofile, checksum = checksum)
        if size is not None:
            exists_size += size
        else:
            error_size += os.path.getsize(ifile)
    else:
        shutil.copyfile(ifile, ofile)
        size = DownloadAndCheck(ifile, ofile, checksum = checksum)
        if size is not None:
            copy_size += size
        else:
            error_size += os.path.getsize(ifile)
    bar.next()

print('\nЗагружено: \t%s\nПроверено: \t%s\nПропущено: \t%s\nОшибки: \t%s\n\n Всего: %s\n' %
      (str_size(copy_size), str_size(exists_size), str_size(miss_size), str_size(error_size), str_size(copy_size + exists_size + miss_size + error_size)))
