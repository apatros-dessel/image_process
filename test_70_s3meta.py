from geodata import *
import argparse

parser = argparse.ArgumentParser(description='Path to vector file')
parser.add_argument('folder_in', help='Path to vector file')
args = parser.parse_args()
folder_in = args.folder_in

def GetS3Scenes(folder_in):
    scenes = OrderedDict()
    for s3id in os.listdir(folder_in):
        folder = fullpath(folder_in, s3id)
        if os.path.isdir(folder):
            meta_path = fullpath(folder, s3id, 'json')
            if os.path.exists(meta_path):
                meta_ds, meta_lyr = get_lyr_by_path(meta_path)
                if meta_lyr:
                    id = meta_lyr.GetNextFeature().GetField('id')
                    scenes[s3id] = (id, meta_path)
                    continue
            print('Cannot find metadata: %s' % s3id)
    return scenes

class Attributes(OrderedDict):

    def GetFromFeature(self, feat, attr_list = None):
        if attr_list is None:
            attr_list = feat.keys()
        for key in attr_list:
            try:
                value = feat.GetField(key)
                if value is not None:
                    self[key] = value
            except KeyError:
                print('KeyError: %s' % key)
            except:
                print('Unreckognized error: %s' % key)

def InspectS3Scene(folder_in):
    report = Attributes()
    s3id = os.path.split(folder_in)[1]
    report['s3id'] = s3id
    meta_path = fullpath(folder_in, s3id, 'json')
    if os.path.exists(meta_path):
        meta_ds, meta_lyr = get_lyr_by_path(meta_path)
        if meta_lyr:
            meta_feat = meta_lyr.GetNextFeature()
            if meta_feat:
                report.GetFromFeature(meta_feat, ['id','id_neuro','datetime','sat_id','channels','type','rows','cols','epsg_dat','x_size','y_size','level','area'])
            else:
                print('METADATA FEATURE NOT FOUND: %s' % s3id)
        else:
            print('CANNOT OPEN METADATA FILE: %s' % s3id)
    else:
        print('METADATA FILE NOT FOUND: %s' % s3id)
    data = False
    data_path = fullpath(folder_in, s3id, 'tif')
    if os.path.exists(data_path):
        raster_data = gdal.Open(data_path)
        if raster_data:
            data = True
    else:
        print('DATA FILE NOT FOUND: %s' % s3id)
    report['data'] = data
    # ql_path = fullpath(folder_in, s3id+'.QL', 'tif')
    # if os.path.exists(ql_path):
        # raster_ql = gdal.Open()

    return report

def CheckIdFromList(info, test_ids, pms=True):
    matched = []
    missed = []
    for test_id in test_ids:
        miss = True
        if pms:
            if re.search('.MS', test_id):
                continue
            elif re.search('_S_', test_id):
                continue
        else:
            if re.search('.PMS', test_id):
                continue
            elif re.search('_PSS4_', test_id):
                continue
        test_id_corr = test_id.replace('*', '.*').replace('3NP2_\d+', '.*')
        fr_search = re.search('^fr\d+_', test_id_corr)
        if fr_search:
            test_id_corr = test_id_corr[len(fr_search.group()):]
        if re.search('\dscn', test_id_corr):
            test_id_corr = test_id_corr.replace('scn', '.SCN')
        for s3id in info:
            id = info[s3id].get('id')
            if id:
                if re.search(test_id_corr, id):
                    matched.append(s3id)
                    miss = False
                    break
            else:
                print('ID not found: %s' % s3id)
                pass
        if miss:
            print(test_id, test_id_corr)
            missed.append(test_id)
    return matched, missed

scenes = GetS3Scenes(folder_in)

info = OrderedDict()
for s3id in scenes:
    info[s3id] = InspectS3Scene(fullpath(folder_in, s3id))

# scroll(info)
# sys.exit()

txts = folder_paths(r'd:\temp',1,'txt')
test_ids = []
for txt_file in txts:
    with open(txt_file) as txt:
        names = txt.read().split('\n')
        test_ids.extend(names)

matched, missed = CheckIdFromList(info, test_ids, pms=False)

scroll(matched, header='MATCHED:', lower='Total matched: %i' % len(matched))
scroll(missed, header='MISSED:', lower='Total missed: %i' % len(missed))
with open(fullpath(folder_in, 'missed.txt'), 'w') as txt:
    txt.write('\n'.join(missed))
