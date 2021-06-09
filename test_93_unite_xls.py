from tools import *

xls_alex = r'C:\Users\Home\Desktop\DEFECTS.xlsx'
xls_sadkov = r'C:\Users\Home\Desktop\errors.xlsx'
xls_fin = r'C:\Users\Home\Desktop\errors_fin2.xls'
files_folder = r'd:\terratech\DEFECTS'
export_folder = r'd:\terratech\DEFECT_FILES'

'''
1) облака, блики камеры, невязки, блики, цветные блики, засветы, ошибка привязки, дефект не найден, съезд по координатам
слабые дефекты изображения (блики, есть практически везде);
2) разлёт, разлёт каналов, цветные полосы, градиент, разъезд каналов
заметные дефекты изображения (есть цветные полосы, с искажениями яркости, но под ними можно разобрать объекты), возможно часть из них - это закрытие разрывов в изображении, иногда это именно так выглядит;
3) разрывы, сплошные полосы, разрыв, сплошной дефект, полоса, полосы, дыра, полоса без канала
частичная утрата изображения (есть чёрные и белые полосы, под которыми не видно изображения, и,или разрывы без данных вообще).
'''

class1 = ['блики','блюминг', 'засветки']
class2 = ['разрывы', 'полосы с утратой изображения']
class3 = ['разъезд каналов']

fixes = {
    'разлёт': 'разъезд каналов',
    # 'блики камеры': 'блики',
    'разрыв': 'разрывы',
    'разлёт каналов': 'разъезд каналов',
    # 'полоса': 'сплошные полосы',
    # 'полосы': 'сплошные полосы',
    'сплошные полосы': 'полосы с утратой изображения',
    'ошибка привязки': 'невязки',
    'зубцы': 'полосы с утратой изображения',
    'дыра': 'разрывы',
    # 'полоса без канала': 'сплошные полосы',
    'съезд по координатам': 'невязки',
    'засветы': 'засветки',
}

export_dict = {
    'class1': {'RP': {'PAN': [], 'MS': []}, 'KV': {'PAN': [], 'MS': []},},
    'class2': {'RP': {'PAN': [], 'MS': []}, 'KV': {'PAN': [], 'MS': []},},
    'class3': {'RP': {'PAN': [], 'MS': []}, 'KV': {'PAN': [], 'MS': []},},
}


def AppendUnique(list_, val_):
    if val_ in globals()['fixes']:
        val_ = globals()['fixes'][val_]
    if val_:
        if not val_ in list_:
            list_.append(val_)
    return list_

def ExtendUnique(list_old, list_new, rename=None):
    if list_new:
        for val_ in list_new:
            list_old = AppendUnique(list_old, val_,)
    return list_old

def SetClass(errors_list):
    for val_ in obj2list(errors_list):
        fin = 1
        class3 = globals()['class3']
        class2 = globals()['class2']
        if val_ in class3:
            return 3
        if val_ in class2:
            fin = 2
    return fin

def DictCounts(dict_, list_):
    for val_ in list_:
        if val_ in dict_:
            dict_[val_] += 1
        else:
            dict_[val_] = 1
    return dict_

class DictLines(OrderedDict):

    def __init__(self, keys):
        for key in keys:
            self[key] = OrderedDict()

    def AppendLines(self, keys, id, line):
        for key in keys:
            if key in self:
                self[key][id] = line

    def Save(self, key, path):
        if key in self:
            dict_to_xls(path, self[key])

sadkov_dict = xls_to_dict(xls_sadkov, 1)
alex_dict = {}#xls_to_dict(xls_alex)

sadkov_errors_list = []
alex_errors_list = []
counts = {}
kv_pan_dict_lines = DictLines(['блики', 'разрывы', 'пропуски микрокадров', 'засветы', 'расфокус', 'сплошные полосы',
                        'цветные полосы', 'разрывы', 'разъезд каналов'])
kv_ms_dict_lines = DictLines(['блики', 'разрывы', 'пропуски микрокадров', 'засветы', 'расфокус', 'сплошные полосы',
                        'цветные полосы', 'разрывы', 'разъезд каналов'])
rp_pan_dict_lines = DictLines(['блики', 'разрывы', 'пропуски микрокадров', 'засветы', 'расфокус', 'сплошные полосы',
                        'цветные полосы', 'разрывы', 'разъезд каналов'])
rp_ms_dict_lines = DictLines(['блики', 'разрывы', 'пропуски микрокадров', 'засветы', 'расфокус', 'сплошные полосы',
                        'цветные полосы', 'разрывы', 'разъезд каналов'])

def GetKanTypeFromID(kan_id):
    if re.search('IM4-.+-.+', kan_id):
        if 'PMS' in kan_id.split('_')[4]:
            return 'PMS'
        else:
            return 'MS'
    else:
        if '.MS' in kan_id:
            return 'MS'
        elif '.PAN' in kan_id:
            return 'PAN'
        elif '.PMS' in kan_id:
            return 'PMS'

for id in sadkov_dict:
    if id:
        if id in alex_dict:
            alex_line = alex_dict.pop(id)
            sadkov_dict[id]['Errors_Alex'] = errors_alex = alex_line.get('Тип дефекта', '')
            sadkov_dict[id]['Спутник'] = alex_line.get('Спутник', '')
            sadkov_dict[id]['Сенсор'] = alex_line.get('Сенсор', '')
            sadkov_dict[id]['Комментарий'] = alex_line.get('Комментарий', '')
            sadkov_dict[id]['Путь'] = alex_line.get('Путь', '')
            # print(errors_alex)
            if errors_alex:
                errors_alex = ExtendUnique([], flist(str(errors_alex).split(','), lambda x: x.strip().lower()))
                sadkov_dict[id]['Errors_Alex'] = errors_alex
                alex_errors_list = ExtendUnique(alex_errors_list, errors_alex)
                counts = DictCounts(counts, errors_alex)
        errors_sadkov = sadkov_dict[id].get('пороки')
        if errors_sadkov:
            errors_sadkov = ExtendUnique([], flist(str(errors_sadkov).split(','), lambda x: x.strip().lower()))
            sadkov_dict[id]['errors'] = errors_sadkov
            sadkov_errors_list = ExtendUnique(sadkov_errors_list, errors_sadkov)
            counts = DictCounts(counts, errors_sadkov)
        #sadkov_dict[id]['class'] = max(SetClass(errors_sadkov), SetClass(errors_alex))
        sadkov_dict[id]['Спутник'] = sat = id[:2]
        type = sadkov_dict[id].get('type')
        if not type:
            type = GetKanTypeFromID(id)
        sadkov_dict[id]['type'] = type
        for error in errors_sadkov:
            if error in class1:
                export_dict['class1'][sat][type] = ExtendUnique(export_dict['class1'][sat][type], [id])
                # print(id, sat, type, error)
            if error in class2:
                export_dict['class2'][sat][type] = ExtendUnique(export_dict['class2'][sat][type], [id])
            if error in class3:
                export_dict['class3'][sat][type] = ExtendUnique(export_dict['class3'][sat][type], [id])
        continue
        if re.search('KV.*PAN', id):
            if errors_alex:
                kv_pan_dict_lines.AppendLines(errors_alex, id, sadkov_dict[id])
            if errors_sadkov:
                kv_pan_dict_lines.AppendLines(errors_sadkov, id, sadkov_dict[id])
        elif re.search('KV.*MS', id):
            if errors_alex:
                kv_ms_dict_lines.AppendLines(errors_alex, id, sadkov_dict[id])
            if errors_sadkov:
                kv_ms_dict_lines.AppendLines(errors_sadkov, id, sadkov_dict[id])
        elif re.search('RP.*PAN', id):
            if errors_alex:
                rp_pan_dict_lines.AppendLines(errors_alex, id, sadkov_dict[id])
            if errors_sadkov:
                rp_pan_dict_lines.AppendLines(errors_sadkov, id, sadkov_dict[id])
        elif re.search('RP.*MS', id):
            if errors_alex:
                rp_ms_dict_lines.AppendLines(errors_alex, id, sadkov_dict[id])
            if errors_sadkov:
                rp_ms_dict_lines.AppendLines(errors_sadkov, id, sadkov_dict[id])
        # print(max(SetClass(errors_sadkov), SetClass(errors_alex)),  id)

if alex_dict:
    scroll(alex_dict, header='Пропущенные файлы', lower='\n')

# scroll(sadkov_errors_list, header='Sadkov', lower='\n')
# scroll(alex_errors_list, header='Alex', lower='\n')

scroll(export_dict, print_type=False, counts=True)

files = folder_paths(files_folder,1,'tif')
names = flist(files, os.path.basename)

for cls in export_dict:
    for sat in export_dict[cls]:
        for type in export_dict[cls][sat]:
            folder_out = r'%s/%s/%s/%s' % (export_folder, sat, type, cls)
            suredir(folder_out)
            for id in export_dict[cls][sat][type]:
                if id in names:
                    copyfile(files[names.index(id)], fullpath(folder_out, id))

# dict_to_xls(xls_fin, sadkov_dict)

sys.exit()

for key in kv_pan_dict_lines:
    if kv_pan_dict_lines[key]:
        scroll(kv_pan_dict_lines[key].keys(), header='KANOPUS PAN %s'%key, lower='Всего %i\n'%len(kv_pan_dict_lines[
                                                                                                     key]))
for key in kv_ms_dict_lines:
    if kv_ms_dict_lines[key]:
        scroll(kv_ms_dict_lines[key].keys(), header='KANOPUS MS %s'%key, lower='Всего %i\n'%len(kv_ms_dict_lines[key]))
for key in rp_pan_dict_lines:
    if rp_pan_dict_lines[key]:
        scroll(rp_pan_dict_lines[key].keys(), header='RESURS PAN %s'%key, lower='Всего %i\n'%len(rp_pan_dict_lines[
                                                                                                     key]))
for key in rp_ms_dict_lines:
    if rp_ms_dict_lines[key]:
        scroll(rp_ms_dict_lines[key].keys(), header='RESURS MS %s'%key, lower='Всего %i\n'%len(rp_ms_dict_lines[key]))
