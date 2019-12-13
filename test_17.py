# Makes composite of several scenes

from image_process import process
from image_processor import scene


path = r''
path2shp = r''
export_dir = r''



class channel:

    def __init__(self, name, scene_id = 0, year = 0, month = 0, day = 0):
        self.name = name
        self.scene_id = scene_id
        self.year = year
        self.month = month
        self.day = day

class composite:

    def __init__(self, name, channels = []):
        self.name = name
        self.channels = []
        self.ids = []
        self.years = []
        for ch in self.channels:
            if ch.scene_id not in self.ids:
               self.ids.append(ch.scene_id)
            if ch.year not in self.years:
                self.years.append(ch.year)
        assert 0 in self.ids
        assert 0 in self.years

    def __len__(self):
        return len(self.channels)

def scenes4composite(scene_list, composite):
    for base_scene in scene_list:
        path2start = []
        for ch in composite.channels:
            if ch.scene_id == 0:
                path2start.append(base_scene.band(ch.name))
            else:
                path2start.append(None)
        if None in path2start:
            base_year = base_scene.meta.date.year
            relevant_scenes = {}
            for year in composite.years:
                relevant_scenes[year] = []
            for scene in scene_list:
                difference = scene.meta.date.year - base_year
                if difference in composite.years:
                    relevant_scenes[year].append(scene)









time_composite = composite('time', [channel('nir'), channel('nir', scene_id = 1, year = -1), channel('green')])

proc = process().input(path)
input = proc.input_list

scene_list = []
for scenepath in proc.input_list:
    scene_list.append(scene(scenepath))
    scene.list[-1].clip(path2shp)



