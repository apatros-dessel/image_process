import os

path = input('Введите путь к папке: ').rstrip('\\') + '\\'

txt_path = input('Укажите путь к индексу, если необходимо: ')

if not txt_path:
    txt_path = path + r'\tif_index.txt'

def FoldersFiles(path, ext = 'tif'):
    files = []
    ext = '.' + ext.lstrip('.')
    for corner, _folders, _files in os.walk(path):
        for file in _files:
            if file.lower().endswith(ext):
                files.append(corner + '\\' + file)
    return files

files = FoldersFiles(path)

with open(txt_path, 'w', encoding='utf8') as txt:
    txt.write('\n'.join(files))

input('%i files found, press Enter to exit' % len(files))
