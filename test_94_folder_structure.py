from tools import *

class FolderDirs(OrderedDict):

    def __init__(self, folder, miss_tmpt=None):
        if os.path.exists(folder):
            for name in os.listdir(folder):
                path = fullpath(folder, name)
                if os.path.isdir(path):
                    if FindAny(path, miss_tmpt, default=False):
                        continue
                    self[name] = path

def ScriptFolder(corner):
    folders = FolderDirs(corner)
    result = OrderedDict()
    for name in folders:
        result[name] = ScriptFolder(folders[name])
    return result

scroll(ScriptFolder(r'\\172.21.195.2\thematic\!razmetka\Kanopus'), empty=False)