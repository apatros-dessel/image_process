from geodata import *
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-r', default='16', dest='region', help='Индекс региона')
parser.add_argument('-f', default = r'\\172.21.195.160\thematic\S3_temp', dest = 'final_dir', help='Путь для сохранения данных')
parser.add_argument('--sat', default='KV', dest='sat', help='Тип спутника (KV, RP)')
parser.add_argument('--sen', default='MS', dest='sensor', help='Тип сенсора (MS, PAN, отсутствует PMS)')
parser.add_argument('--part', default=0.1, dest='part', help='Доля загружаемых снимков')
parser.add_argument('--dir', default=None, dest='direct', help='Путь к локальному хранилищу данных')

args = parser.parse_args()
index_list = args.region.split(',')
final_dir = args.final_dir
sat = args.sat
sensor = args.sensor
direct = args.direct
part = float(args.part)

class Downloader:

    def __init__(self, path, sat='KV', sensor='MS', direct=None):
        self.path = path
        self.name = os.path.split(path)[1]
        self.sat = sat
        self.sensor = sensor
        self.categories = {'':[]}
        self.satname = {'KV': 'kanopus', 'RP': 'resurs'}.get(sat, 'kanopus')
        self.skip = []
        self.miss_categories = ['used']
        self.direct = direct

    def xls(self):
        xls_path = fullpath(self.path, self.name, 'xls')
        if os.path.exists(xls_path):
            return xls_to_dict(xls_path)

    def xls_out(self, dict_):
        xls_path = r'%s/%s_%s_%s.xls' % (self.path, self.name, self.sat, self.sensor)
        dict_to_xls(xls_path, dict_)

    def ql_paths(self):
        corner_path = r'%s/%s/%s' % (self.path, self.sat, self.sensor)
        return folder_paths(corner_path,1,'jpg')

    def update_category(self, cat, id):
        if cat in self.categories:
            self.categories[cat].append(id)
        elif re.search('^%s' % self.sat, cat):
            return None
        else:
            self.categories[cat] = [id]

    def update_categories(self):
        # xls_dict = self.xls()
        ql_paths = self.ql_paths()
        for ql_path in ql_paths:
            dir, id = os.path.split(ql_path)
            cat = os.path.split(dir)[1]
            if cat==self.sensor:
                cat = ''
            self.update_category(cat, id)

    def set_skip(self, txt_path=r'\\172.21.195.2\thematic\!razmetka\id_list.txt'):
        txt = open(txt_path)
        if txt is not None:
            self.skip.append(txt.read().split('\n'))

    def download(self, folder, part=0.1):
        xls_dict = self.xls()
        for cat in self.categories:
            if cat in self.miss_categories:
                print('CATEGORY MISSED: %s' % cat)
                continue
            cat_length = len(self.categories[cat])
            upload_length = int(cat_length*part)
            i = 0
            for ql_id in self.categories[cat]:
                params = xls_dict.get(ql_id)
                if params is None:
                    print('ID NOT FOUND: %s' % ql_id)
                    continue
                params['Category'] = cat
                scene_id = '_'.join(ql_id.split('_')[:-1]) + '.L2'
                if i>upload_length:
                    params['Status'] = 'PASSED'
                elif scene_id in self.skip:
                    params['Status'] = 'SKIPPED'
                else:
                    path = params.get('Path')
                    if path is None:
                        params['Status'] = 'ERROR 1'
                    else:
                        short_path, folder_id = os.path.split(path)
                        postavka = re.search(r'natarova', short_path)
                        if postavka is None:
                            params['Status'] = 'ERROR 2'
                        elif self.direct is not None:
                            direct_path = fullpath(direct, path.split('natarova')[-1])
                            upload_folder = r'%s%s' % (folder, short_path.split('natarova')[-1])
                            print(direct_path, upload_folder)
                            copydir(direct_path, upload_folder)
                            if os.path.exists(fullpath(upload_folder, folder_id)):
                                params['Status'] = 'DOWNLOADED'
                                i += 1
                            else:
                                print('ERROR COPYING: %s' % scene_id)
                        else:
                            # postavka = postavka.group()
                            # upload_folder = r'%s%s%s' % (folder, postavka, short_path.split(postavka)[-1])
                            upload_folder = r'%s%s' % (folder, short_path.split('natarova')[-1])
                            suredir(upload_folder)
                            result =  DownloadFromDB(scene_id, self.satname, upload_folder, check_folder=folder_id)
                            if result:
                                params['Status'] = 'DOWNLOADED'
                                i += result
                            else:
                                print('ERROR DOWNLOADING: %s' % scene_id)
                                params['Status'] = 'ERROR 3'
                xls_dict[ql_id] = params
        self.xls_out(xls_dict)

def DownloadFromDB(id, sat, folder, check_folder=None):
    # gu_db_query -w "source='kanopus' and hashless_id='KV1_31707_25285_00_KANOPUS_20180409_091320_091401.SCN2.MS.L2'" - d \\172.21.195.160\thematic\S3_temp
    result = 0
    if check_folder is None:
        command = r'''gu_db_query -w "source='%s' and hashless_id='%s'" -d %s''' % (sat, id, folder)
        os.system(command)
        result = 1
    else:
        temp_folder = tempname()
        command = r'''gu_db_query -w "source='%s' and hashless_id='%s'" -d %s''' % (sat, id, temp_folder)
        os.system(command)
        for n in os.listdir(temp_folder):
            if n==check_folder:
                copydir(fullpath(temp_folder, n), folder)
                result = 1
                break
        destroydir(temp_folder)
    return result

# DownloadFromDB('KVI_15015_10756_01_KANOPUS_20200329_071237_071317.SCN8.MS.L2', 'kanopus', final_dir, check_folder='KVI_15015_10756_01_KANOPUS_20200329_071237_071317.SCN8.MS_dc07baffd20359244af5f8e84509e4de6cd49a1d')
for index in index_list:
    index_path = r'\\172.21.195.2\thematic\!SPRAVKA\S3\\' + index
    if not os.path.exists(index_path):
        print('PATH NOT FOUND: %s\nUNABLE TO FIND QL' % index_path)
        continue
    downloader = Downloader(index_path, sat=sat, sensor=sensor, direct=direct)
    # downloader.set_skip()
    downloader.update_categories()
    downloader.download(final_dir, part=part)
sys.exit()
