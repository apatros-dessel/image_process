from geodata import *

path_in = r'd:\export'

files = folder_paths(path_in, files=True, extension='json')

errors = []

successes = []

print('Start renaming %i files' % len(files))

for i, file in enumerate(files):
    new_data = None
    '''
    ds_in, lyr_in = get_lyr_by_path(file, 1)

    feat = lyr_in.GetNextFeature()
    txt = feat.GetField('datetime')
    new_txt = 'fsdasvsfd' + txt.replace(r'/','-').replace(' ', 'T')

    print('{}: {}'.format(os.path.basename(file), new_txt))

    # feat.UnsetField('datetime')
    feat.SetFieldString(20, 'datetime')
    print(feat.GetFieldDefnRef('datetime').GetType())
    feat.SetField('datetime', new_txt)
    print(feat.GetField('datetime'))
    print(feat.GetFieldDefnRef('datetime').GetType())

    field_defn = ogr.FieldDefn('datetime', 4)
    lyr_in.AlterFieldDefn(lyr_in.GetFieldIndex('datetime'), field_defn)

    lyr_in.SetFeature(feat)
    ds_in = None
    '''
    data = open(file, 'r').read()
    try:
        dtime = re.search(r'"datetime": "[^"]+"', data).group()[13:-1]
        new_dtime = dtime.replace(u'\\/','-').replace(' ', 'T')
        new_data = data.replace(dtime, new_dtime)
    except:
        errors.append(os.path.basename(file))

    if new_data is not None:
        json = open(file, 'w')
        json.write(new_data)
        json = None
        successes.append(os.path.basename(file))

scroll(successes, header='Files successfully written:')

scroll(errors, header='Errors:')

print('%i files found' % len(files))
print('%i files successfully written' % len(successes))
print('%i errors' % len(errors))

def json_fix_datetime(file):
    data = open(file, 'r').read()
    dtime = re.search(r'"datetime": "[^"]+"', data).group()[13:-1]
    new_dtime = dtime.replace(u'\\/', '-').replace(' ', 'T')
    new_data = data.replace(dtime, new_dtime)
    if new_data is not None:
        json = open(file, 'w')
        json.write(new_data)
        json = None
