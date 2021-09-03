from tools import *

class FolderDirs(OrderedDict):

    def __init__(self, folder, miss_tmpt=None):
        if os.path.exists(folder):
            if script_files:
                files = []
            for name in os.listdir(folder):
                path = fullpath(folder, name)
                if os.path.isdir(path):
                    if FindAny(path, miss_tmpt, default=False):
                        continue
                    self[name] = path
                elif script_files:
                    files.append(name)
            if script_files:
                with open(r'%s\files.txt' % folder, 'w') as txt:
                    txt.write('\n'.join(files))

def ScriptFolder(corner, extensions=None):
    folders = FolderDirs(corner)
    result = OrderedDict()
    if folders:
        for name in folders:
            result[name] = ScriptFolder(folders[name])
        return result
    else:
        FilesInfo(corner)
        return len(folder_paths(corner, 1, ['shp', 'tif']))

def FilesInfo(folder):
    if os.path.exists(folder):
        with open(r'%s\files.txt' % folder, 'w') as txt:
            txt.write('\n'.join(os.listdir(folder)))

scroll(ScriptFolder(r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\Resurs_geoton_snow'), empty=False)