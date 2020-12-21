# Reproject Kanopus source data and prepear for uploading to S3 server

from geodata import *
from image_processor import process, scene
from ip2s3 import *

folder_in = r'\\172.21.195.215\thematic\source\ntzomz\102_2020_1339'
folder_out = r'd:\rks\s3\kanopus_check'
references_path = r'\\172.21.195.215\thematic\products\ref\_reference'
# test_ids_txt = r'\\172.21.195.215\thematic\products\s3\kanopus\missed_pms.txt'
folder_s3 = r'\\172.21.195.215\thematic\products\s3\kanopus'
v_cover = r''
imsys_list = ['KAN', 'RSP']
pms = False
overwrite = False
report_path = None

'''
STAGES
1. Find all scenes available in source data sorting them by location and image type (PAN, MS, PMS)
2. Check if some of the scenes are already processed
3. Reproject source images from PMS data
4. If PMS data is not available, reproject PAN and MS and make pansharpening
5. Prepare PMS data for S3
6. If reprojection was failed, save the source data separately
'''

reference_list = folder_paths(references_path,1,'tif')
# test_ids = open(test_ids_txt).read().split('\n')

if report_path is None:
    for report_ in ('report', 'report_alex', 'report_serg'):
        if os.path.exists(fullpath(folder_in, report_, 'xls')):
            report_path = fullpath(folder_in, report_, 'xls')
            break
xls_quicklook_dict = xls_to_dict(report_path)

source_scenes, v_cover = FindScenes(folder_in, imsys_list=imsys_list, v_cover=v_cover, skip_duplicates=False)
if len(source_scenes)==0:
    print('No source scenes found in %s' % folder_in)
    sys.exit()
s3_scenes = GetS3Scenes(folder_s3)
matched, unmatched = GetUnmatchingScenes(source_scenes, s3_scenes)
unmatched, errored = GetQuicklookCheck(unmatched, xls_quicklook_dict, type=['MS'])

# match, miss = CheckIdFromList(unmatched, test_ids, pms=True)

# scroll(unmatched, lower=len(unmatched))
name = os.path.split(folder_in)[1]
matched_list = list(matched.keys())
# scroll(matched_list, lower=len(matched_list))
suredir(folder_out)
with open(fullpath(folder_out, 'DONE__'+name, 'txt'), 'w') as txt:
    txt.write('\n'.join(matched_list))
unmatched_list = list(unmatched.keys())
# scroll(unmatched_list, lower=len(unmatched_list))
if errored is None:
    with open(fullpath(folder_out, 'NOT_CHECKED__'+name, 'txt'), 'w') as txt:
        txt.write('\n'.join(unmatched_list))
else:
    with open(fullpath(folder_out, 'IN_PROCESS__'+name, 'txt'), 'w') as txt:
        txt.write('\n'.join(unmatched_list))
    errored_list = list(errored.keys())
    with open(fullpath(folder_out, 'SKIPPED__'+name, 'txt'), 'w') as txt:
        txt.write('\n'.join(errored_list))

sys.exit()
success = []
fail = []
s3_folder = fullpath(folder_out, 's3')
for id in unmatched:
    # if id in match:
        # print(id)
        # continue
        res = ReprojectSystem(unmatched[id], reference_list, folder_out, pms=pms, overwrite=overwrite)
        if not pms:
            id = id.replace('.PMS', '.MS')
        if res:
            success.append(id)
            if isinstance(res, str):
                Scene4S3(res, v_cover, s3_folder, id, rgb_band_order=[1,2,3], save_rgb=False, ms2pms=False)
        else:
            # fail.append(id)
            pass
        print('EMPTY TDIR')
        globals()['temp_dir_list'].empty()
        print('EMPTY TDIR_GEO')
        globals()['temp_dir_list_geo'].empty()
sys.exit()

scroll(success, header='SUCCESS', lower=len(success))
scroll(fail, header='FAIL', lower=len(fail))