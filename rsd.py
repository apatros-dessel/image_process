from geodata import *
from image_processor import scene as Scene
from image_processor import template_dict

import argparse

parser = argparse.ArgumentParser(description='Индексировать ДДЗ')
parser.add_argument('-o', default=None, dest='pold', help='Путь к уже существующему индексу')
parser.add_argument('pin', help='Путь для поиска масок')
parser.add_argument('pout', help='Путь для сохранения файла индекса')

class SceneData:

    def __init__(self, imsys, setid, setpath, sceneid, scenepath, date, limits):
        self.imsys = imsys
        self.setid = setid
        self.setpath = setpath
        self.sceneid = sceneid
        self.scenepath = scenepath
        self.date = date
        self.limits = limits

    def Path(self):
        return r'%s\%s' % (self.setpath, self.scenepath)

    def Available(self):
        return os.path.exists(self.Path())

    def Scene(self):
        if self.Available():
            scene = Do(Scene, self.Path())
            return scene

    def Dict(self):
        dict_ = OrderedDict()
        dict_['imsys'] = self.imsys
        dict_['setid'] = self.setid
        dict_['setpath'] = self.setpath
        dict_['sceneid'] = self.sceneid
        dict_['scenepath'] = self.scenepath
        dict_['date'] = self.date
        dict_['limits'] = self.limits
        return dict_

    def List(self):
        return [self.imsys, self.setid, self.setpath, self.sceneid, self.scenepath, self.date, self.limits]

    def String(self):
        return ';'.join(flist(self.List(), str))

def GetSceneData(scene, setid = '', setpath = ''):
    imsys = scene.imsys
    sceneid = scene.meta.id
    scenepath =  scene.fullpath
    if len(setpath)>0:
        if scenepath.startswith(setpath):
            scenepath = scene.fullpath[len(setpath)]
    date = scene.meta.name('[date]')
    limits = None
    cover_path = scene.datamask()
    if cover_path:
        din, lin = get_lyr_by_path(cover_path)
        if lin:
            limits = lin.GetExtent()
    return SceneData(imsys, setid, setpath, sceneid, scenepath, date, limits)

def GetSceneDataFromString(str_):
    data = str_.split(';')
    if len(data)==7:
        return SceneData(data)

class RemoteSensingData(OrderedDict):

    def __init__(self):
        self.idlim = 0
        self.templates = globals()['template_dict']

    def StrIter(self):


    def AddSceneData(self, scene_path, setid = '', setpath = ''):
        file = os.path.basename(scene_path)
        for imsys in self.templates:
            template = self.templates[imsys]
            if re.search(template, file):
                scene = Do(Scene, scene_path, imsys)
                if scene:
                    scene_data = Do(GetSceneData, scene)
                    if scene_data:
                        self[self.isdlim] = scene_data
                        self.idlim += 1
                        return self

    def AddStringData(self, str_):
        scene_data = GetSceneDataFromString(str_)
        if scene_data:
            self[self.isdlim] = scene_data
            self.idlim += 1
            return self

    def SaveRSD(self, csv_path):
        dict_to_csv(csv_path, RemoteSensingDataIter(self))

class RemoteSensingDataIter:

    def __init__(self, remote_sensing_data):
        self.dict = remote_sensing_data
        self.keys = list(remote_sensing_data.keys)
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        key = self.keys[self.count]
        self.count += 1
        return self.dict.get(key).String()

    def next(self):
        return self.__next__()

def GetRemoteSensingDataFromCSV(path):



