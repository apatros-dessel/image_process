from geodata import *
import argparse

parser = argparse.ArgumentParser(description='Обновлять данные в хранилище')
parser.add_argument('corner', help='Корневой путь к хранилищу')
args = parser.parse_args()
corner = args.corner


def WriteLog(path, logstring):
    datestring = str(datetime.now()).rstrip('0123456789').replace(' ','_').replace(':','-')
    datelogstring = '%s %s\n' % (datestring, logstring)
    style = ('w','a')[os.path.exists(path)]
    with open(path,style) as txt:
        txt.write(datelogstring)



class FolderDirs(dict):

    def __init__(self, folder, miss_tmpt=None):
        for name in os.listdir(folder):
            path = folder_paths(folder, name)
            if os.path.isdir(path):
                if miss_tmpt:
                    if re.search(miss_tmpt, name):
                        continue
                self[name] = path

class FolderFiles(dict):

    def __init__(self, folder, miss_tmpt=None, type=None):
        if type is not None:
            typelist = obj2list(type)
        else:
            typelist = None
        for name in os.listdir(folder):
            path = folder_paths(folder, name)
            if os.path.isfile(path):
                if typelist is not None:
                    for _type in typelist:
                        if name.lower().endswith(_type):
                            self[name] = path
            elif miss_tmpt:
                if re.search(miss_tmpt, name):
                    new_paths = FolderFiles(path)
                    if new_paths:
                        for new_name in new_paths:
                            self[r'%s/%s' % (name, new_name)] = new_paths[new_name]

class MaskSubtypeFolderIndex(dict):

    def __init__(self, corner, subtype):
        self.corner_dir = corner
        self.subtype = subtype
        datacats = globals()['datacats']
        for datacat in datacats:
            self.Fill(datacat)

    def Fill(self, datacat):
        datacats = globals()['datacats']
        if datacat in datacats:
            datacatpath = r'%s/%s/%s' % (self.corner, datacat, self.subtype).rstrip(r'\/')
            if os.path.exists(datacatpath):
                self[datacat] = FolderFiles(datacatpath, miss_tmpt='&', type=datacats[datacat])
        else:
            print('WRONG DATACAT: %s' % datacat)

    def __len__(self):
        return max(flist(self.values(), len))

    def __bool__(self):
        return bool(len(self))

class MaskTypeFolderIndex:

    def __init__(self, corner):
        self.corner = corner
        self.FillMaskBandclasses()
        self.FillMaskSubtypes()

        mask_type_dirs = FolderDirs(corner)
        for datacat in globals()['datacats']:
            if not datacat in mask_type_dirs:
                print('WRONG DATACAT: %s' % datacat)
                return None

    def FillMaskBandclasses(self):
        self.bandclasses = {}
        bandclasses = globals()['bandclasses']
        for bandclass in bandclasses:
            bandclasspath = r'%s/%s' % (self.corner, bandclass)
            if os.path.exists(bandclasspath):
                self.bandclasses[bandclass] = bandclasspath

    def FillMaskSubtypes(self):
        datacats = globals()['datacats']
        subtypes = {'': None}
        for bandclass in self.bandclasses:
            bandclasspath = self.bandclasses[bandclass]
            for datacat in datacats:
                datacatpath = r'%s/%s' % (bandclasspath, datacat)
                subtypedirs = FolderDirs(datacatpath, miss_tmpt='&')
                if subtypedirs is not None:
                    subtypes.update(subtypedirs)
        self.subtypes = {}
        for subtype in subtypes.keys():
            subtype_index = MaskSubtypeFolderIndex(self.corner, subtype)
            if subtype_index:
                self.subtypes[subtype] = subtype_index
