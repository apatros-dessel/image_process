from geodata import *
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('index_path', help='Путь к папке с квиклуками')
parser.add_argument('final_dir', help='Путь для сохранения данных')
parser.add_argument('-d', default=None, dest='dout', help='Путь для сохранения сцен с метаданными')
parser.add_argument('-r', default=None, dest='rdir', help='Путь к папке с растровыми файлами, пересечение с которыми тоже выкачивать безотносительно имени')
args = parser.parse_args()
dout = args.dout
rdir = args.rdir
index_path = args.index_path
final_dir = args.final_dir

class GetFolder:

    def __init__(self, path, sat='KV', sensor='MS'):
        self.path = path
        self.name = Name(path)
        self.sat = sat
        self.sensor = sensor
        self.categories = {'':[]}

    def xls(self):
        xls_path = fullpath(self.path, self.name, 'xls')
        if os.path.exists(xls_path):
            return xls_to_dict(xls_path)

    def ql_paths(self):
        corner_path = r'%s/%s/%s' % (self.path, self.sat, self.cat)
        return folder_paths(corner_path,1,'jpg')

    def update_category(self, cat, id):
        if cat in self.categories:
            self.categories[cat].append(id)
        else:
            self.categories[cat] = [id]

    def update_categories(self):
        # xls_dict = self.xls()
        ql_paths = self.ql_paths()
        for ql_path in ql_paths:
            dir, id = os.path.split(ql_path)
            cat = Name(dir)
            if cat==self.sensor:
                cat = ''
            self.update_category(cat, id)



def ExtractKanId(line):
    if re.search('^KV.+L2$', line):
        return line
    else:
        for type in ['.MS', '.PAN', '.PMS']:
            if type in line:
                return line.split(type)[0]+type+'.L2'

def KanCallSQL(kan_id, type=False):
    if re.search('IM4-.+-.+', kan_id):
        if type:
            date = kan_id.split('-')[2]
            kan_date = '%s-%s-%s' % (date[:4], date[4:6], date[6:])
            return '''"source='kanopus' and date(datetime)='%s' and type='%s'"''' % (kan_date, type.lower())
        else:
            print('KANOPUS TYPE NOT DEFINED, CANNOT DOWNLOAD DATA: %s' % kan_id)
    else:
        return '''"source='kanopus' and hashless_id='%s'"''' % kan_id

def DownloadKanopusFromS3(pout, type=None, geom_path = None):
    command = r'''gu_db_query -w "source='kanopus' and type='ms'" -d %s''' % pout
    if geom_path is not None:
        command += ' -v %s' % geom_path
    print(command)
    os.system(command)

class FolderDirs(dict):

    def __init__(self, folder, miss_tmpt=None):
        for name in os.listdir(folder):
            path = fullpath(folder, name)
            if os.path.isdir(path):
                if miss_tmpt:
                    if re.search(miss_tmpt, name):
                        continue
                self[name] = path

suredir(final_dir)

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
    path0 = tempname()
    raster_fin = fullpath(final_dir,id,'tif')
    if os.path.exists(raster_fin):
        print('FILE EXISTS: %s' % id)
        continue
    command = r'''gu_db_query -w "source='kanopus' and hashless_id='%s'" -d %s''' % (id, path0)
    os.system(command)
    dirs = FolderDirs(path0)
    if dirs:
        for folder in dirs:
            imgid = ExtractKanId(folder)
            raster = folder_paths(dirs[folder],1,'tif')[0]
            raster_fin = fullpath(final_dir,imgid,'tif')
            copyfile(raster, raster_fin)
            if dout is not None:
                copydir(dirs[folder], dout)
            print('WRITTEN: %s\n' % id)
    else:
        print('EMPTY DIRS: %s\n' % id)
    destroydir(path0)

if rdir and dout:
    rfiles = folder_paths(rdir,1,'tif')
    scroll(rfiles)
    for rfile in rfiles:
        rmask = tempname('json')
        RasterLimits(gdal.Open(rfile), reference=None, vector_path=rmask)
        if os.path.exists(rmask):
            f = r'%s\!_new' % (dout)
            suredir(f)
            DownloadKanopusFromS3(f, geom_path = rmask)
            print('UPLOADED: %s' % rfile)
        delete(rmask)

