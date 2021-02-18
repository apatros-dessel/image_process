from tools import *
import pandas as pd

index_path = r'\\172.21.195.2\thematic\!SPRAVKA\S3\16\snowy.xlsx'
dout = None
final_dir = r'e:\rks\qltest'
suredir(final_dir)

def ExtractKanId(line):
    return line.split('MS')[0]+'MS.L2'

class FolderDirs(dict):

    def __init__(self, folder, miss_tmpt=None):
        for name in os.listdir(folder):
            path = fullpath(folder, name)
            if os.path.isdir(path):
                if miss_tmpt:
                    if re.search(miss_tmpt, name):
                        continue
                self[name] = path

if index_path.endswith('txt'):
    with open(index_path) as txt:
        lines = txt.read().split('\n')
elif index_path.endswith('xls'):
    lines = []
    for xls_line in xls_to_dict(index_path):
        id_source = xls_line.get('ID')
        if id_source:
            lines.append(id_source)
elif index_path.endswith('xlsx'):
    lines = []
    for id_source in pd.read_excel(index_path).get('ID'):
        if id_source:
            lines.append(id_source)

for line in lines:
    id = ExtractKanId(line)
    if dout is None:
        path0 = tempname()
    else:
        path0 = dout
        suredir(path0)
    command = r'''gu_db_query -w "source='kanopus' and hashless_id='%s'" -d %s''' % (id, path0)
    os.system(command)
    dirs = FolderDirs(path0)
    for folder in dirs:
        imgid = ExtractKanId(folder)
        raster = folder_paths(dirs[folder],1,'tif')[0]
        raster_fin = fullpath(final_dir,imgid,'tif')
        shutil.copyfile(raster, raster_fin)
        print('WRITTEN: %s\n' % id)
    destroydir(path0)
