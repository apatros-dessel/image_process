from geodata import *
import argparse

parser = argparse.ArgumentParser(description='Razmetka creation options')
parser.add_argument('--reorder', default=None, dest='reorder',  help='Изменить порядок каналов в конечном файле')
parser.add_argument('xls', help='Путь к файлу с результатами проверки')
parser.add_argument('dout', help='Путь к папке для сохранения файлов')
parser.add_argument('vals', help='Перечень значений mark, кои нужно сохранять')
args = parser.parse_args()

def GetValsList(vals_str):
    vals_list = []
    vals = vals_str.split(',')
    for val in vals:
        if re.search('^\d+$', val):
            vals_list.append(int(val))
        elif re.search('^\d+-\d+$', val):
            basevals = val.split('-')
            vals_list.extend(list(range(int(basevals[0]), int(basevals[1])+1)))
        else:
            print('CANNOT PROCESS VAL: "%s"' % val)
    return vals_list

proverka = xls_to_dict(args.xls)
suredir(args.dout)
vals_list = GetValsList(args.vals)
reorder = args.reorder
if reorder is not None:
    reorder = flist(reorder.split(','), int)
# scroll(vals_list)

for path in proverka:
    mark = int(proverka[path].get('mark'))
    if mark in vals_list:
        id = proverka[path].get('id')
        if id is not None:
            folder_in = os.path.split(path)[0]
            file_in = folder_paths(folder_in,1,'tif')[0]
            if reorder is None:
                copyfile(file_in, fullpath(args.dout, id, 'tif'))
            else:
                SaveRasterBands(file_in, reorder, fullpath(args.dout, id, 'tif'), options={'compress': 'DEFLATE'}, overwrite=True)
            print('SAVED: %s' % id)
