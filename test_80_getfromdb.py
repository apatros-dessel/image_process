from tools import *

txt_path = r'C:\Users\admin\Downloads\snow2.txt'
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

with open(txt_path) as txt:
    for line in txt.read().split('\n'):
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
