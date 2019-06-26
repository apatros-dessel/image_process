# Describes class process.py

from service import *
from scene import *


# Checks if the file name fits the image system
def corner_file_check(filename, template):
    if re.search(template, filename) is not None:
        return True
    else:
        return False

class process(object):

    def __init__(self, input_path='', output_path='', image_system = 'Landsat', image_id = 'L8OLI', work_method = 'Single', ath_corr_method = 'None', return_bands = False, filter_clouds = False):
        self.input_path = input_path #
        self.output_path = output_path # must be dir
        self.image_system = image_system
        #self.image_id = image_id
        self.work_method = work_method
        self.ath_corr_method = ath_corr_method
        self.return_bands = return_bands
        self.filter_clouds = filter_clouds
        self.input_list = []
        self.scene = [] # contains scenes
        self.branch = {} # contains procedures
        self.corner_file_list = {
            'Landsat': 'LC\d\d_.+_MTL\.txt',
            'Sentinel': 'MTD_MSIL1C\.xml',
        }

    def __repr__(self):
        return 'Object of class "process" with\n input_path: {i_p}\n image_system: {i_s}\n work method: {w_m}\n athmospheric correction method: {a_c_m}\n return bands: {r_b}\n filter clouds: {f_c}\n {n_sc} scenes are now available'.format(i_p=self.input_path, i_s=self.image_system, w_m=self.work_method, a_c_m=self.ath_corr_method, r_b=self.return_bands, f_c=self.filter_clouds, n_sc=len(self.input_list))

    def __str__(self):
        return '{i_s} process.py of {n_sc} scenes available.'.format(i_s=self.image_system, n_sc=len(self.input_list))

    # Returns number of paths in the input_list
    def __len__(self):
        return len(self.input_list)

    def __lt__(self, other):
        return len(self) < len(other)

    def __le__(self, other):
        return len(self) <= len(other)

    def __eq__(self, other):
        return len(self) == len(other)

    def __ne__(self, other):
        return len(self) != len(other)

    def __gt__(self, other):
        return len(self) > len(other)

    def __ge__(self, other):
        return len(self) >= len(other)

    # Checks if a single path is available in the input_list. If the list is empty fills it with self.input()
    def __bool__(self):
        if self.input_list == []:
            self.input()
        for s_path in self.input_list:
            if os.path.exists(s_path):
                return True
        return False

    def __iadd__(self, other):
        other_ = str(other)
        if os.path.exists(other_):
            if os.path.isdir(other_):
                raise Exception('Path to scene must be file, not dir: {}'.format(other_))
            if other_ in self.input_list:
                print('Input in the list: {}'.format(other_))
            else:
                self.input_list.append(other_)
                self.scene.append(None)
        else:
            print('Path not found')
        return self

    def __isub__(self, other):
        if isinstance(other, int):
            self.scene.pop(other)
            self.input_list.pop(other)
        elif isinstance(other, str):
            other_ = str(other)
            if other_ in self.input_list:
                self.scene.pop(self.input_list.index(other_))
                self.input_list.remove(other_)
            else:
                print('Not found in the input list: {}'.format(other_))
        else:
            print('Unexpected argument: type(other) = {}'.format(type(other)))
        return self

    # Returns scene by index
    # If index is negative closes the scene
    def __getitem__(self, item):
        item = self.check_scene_id(item)
        if item < 0:
            item = len(self) + item
        if self.scene[item] is None:
            self.open_scene(item)
        return self.scene[item]

    # Fills self.input_path list with paths to scenes
    def input(self):
        if '" "' in self.input_path:
            self.work_method = 'By_List'
        elif os.path.isdir(self.input_path):
            self.work_method = 'Bulk'
        if self.input_path == '':
            raise Exception('No input_path found')
        elif not os.path.exists(self.input_path):
            raise Exception('Cannot find the input path: {}'.format(self.input_path))
        self.input_list = []
        if self.work_method == 'Single':
            self += self.input_path
        elif self.work_method == 'Bulk':
            to_input = walk_find(self.input_path, self.corner_file_list[self.image_system])
            for path in to_input:
                self += path
        elif self.work_method == 'By_List':
            input = re.strip(self.input_path)
            for i in range(len(input)):
                if (input[i].startswith('"') and input[i].endswith('"')):
                    input[i] = input[i][1:-1]
                self += input[i]
        return self

    # Checks validity of scene_id value to the process
    def check_scene_id(self, id):
        try:
            id = int(id)
        except:
            raise TypeError('Cannot convert scene_id to int: {}'.format(id))
        if abs(id) > len(self):
            raise IndexError('Scene index out of range: {}'.format(id))
        return id

    # Opens one scene
    def open_scene(self, scene_id=0):
        scene_id = self.check_scene_id(scene_id)
        if self.scene[scene_id] is None:
            self.scene[scene_id] = scene(self.input_list[scene_id])
        return self.scene[scene_id]

    # Closes one scene
    def close_scene(self, scene_id=0):
        scene_id = self.check_scene_id(scene_id)
        self.scene[scene_id] = None
        return None

    # Opens many scenes
    def open_scenes(self, open_list=None, except_list=None):
        if open_list is None:
            open_list = list(range(len(self)))
        if except_list is None:
            except_list = []
        for key in range(len(self)):
            if key not in except_list:
                self.open_scene(key)
        return None

    # Closes many scenes
    def close_scenes(self, close_list=None, except_list=None):
        if close_list is None:
            close_list = list(range(len(self)))
        if except_list is None:
            except_list = []
        for key in range(len(self)):
            if key not in except_list:
                self.close_scene(key)
        return None

    def ndvi_procedure(self, scene_id=0):
        s = self[scene_id]
        if s:
            s.ndvi(self.ath_corr_method)
            os.chdir(self.output_path)
            data_ids = ['NDVI_{}'.format(self.ath_corr_method)]
            filenames = ['{}_NDVI_{}.tif'.format(s.descript, self.ath_corr_method)]
            mask_0 = []
            if self.filter_clouds:
                if self.image_system == 'Landsat':
                    s.mask('QUALITY', 2720, True, 'Cloud')
                elif self.image_system == 'Sentinel':
                   vector_path = s.meta_call('MASK_FILENAME', check={'type': 'MSK_CLOUDS'}, mtd=True)
                   vector_path = '{}\\{}'.format(s.folder, vector_path)
                   if os.path.exists(vector_path):
                       s.vector_mask(vector_path, 'Cloud', data_id='4')
                   else:
                       print('Vector mask not found: {}'.format(vector_path))
                mask_0.append('Cloud')
            bands = {'Landsat': ['4', '5'], 'Sentinel': ['4', '8']}[self.image_system]
            mask = [mask_0 + bands]
            if self.return_bands:
                if self.ath_corr_method == 'None':
                    add = 'Ref'
                else:
                    add = self.ath_corr_method
                for band in bands:
                    data_ids.append('{}_{}'.format(band, add))
                    filenames.append('{}_B{}_{}.tif'.format(s.descript, band, add))
                    mask.append(mask_0 + [band])
            for id in range(len(data_ids)):
                s.save(data_ids[id], filenames[id], mask[id])
        else:
            print('No data found in {}'.format(str(s)))
        return None

    def run(self, procedure_list, delete_scenes=True):
        procedures = {
            'ndvi': self.ndvi_procedure,
        }
        if isinstance(procedure_list, str):
            procedure_list = [procedure_list]
        for procedure in procedure_list:
            if procedure not in procedures:
                raise Exception('No procedure found: {}'.format(procedure))
        self.input()
        for scene_id in range(len(self.input_list)):
            for procedure in procedure_list:
                procedures[procedure](scene_id)
            if delete_scenes:
                self.close_scene(scene_id)

