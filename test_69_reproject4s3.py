# Reproject Kanopus source data and prepear for uploading to S3 server

from geodata import *
from image_processor import process, scene
from ip2s3 import *

folder_in = r'\\172.21.195.215\thematic\source\ntzomz\102_2020_1913_new'
folder_out = r'd:\rks\s3\kanopus_missed\1913new_MS'
references_path = r'\\172.21.195.215\thematic\products\ref\_reference'
# test_ids_txt = r'\\172.21.195.215\thematic\products\s3\kanopus\missed_pms.txt'
folder_s3 = r'\\172.21.195.215\thematic\products\s3\kanopus'
v_cover = r''
imsys_list = ['KAN']
pms = True
overwrite = False

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

source_scenes, v_cover = FindScenes(folder_in, imsys_list=imsys_list, v_cover=v_cover)
if len(source_scenes)==0:
    print('No source scenes found in %s' % folder_in)
    sys.exit()
s3_scenes = GetS3Scenes(folder_s3)
matched, unmatched = GetUnmatchingScenes(source_scenes, s3_scenes)

# match, miss = CheckIdFromList(unmatched, test_ids, pms=True)

scroll(unmatched, lower=len(unmatched))
name = os.path.split(folder_in)[1]
matched_list = list(matched.keys())
scroll(matched_list, lower=len(matched_list))
with open(fullpath(folder_out, name+'_matched', 'txt'), 'w') as txt:
    txt.write('\n'.join(matched_list))
unmatched_list = list(unmatched.keys())
scroll(unmatched_list, lower=len(unmatched_list))
with open(fullpath(folder_out, name+'_missed', 'txt'), 'w') as txt:
    txt.write('\n'.join(unmatched_list))

success = []
fail = []
s3_folder = fullpath(folder_out, 's3')
for id in unmatched:
    # if id in match:
        # print(id)
        # continue
        res = ReprojectSystem(unmatched[id], reference_list, folder_out, pms=pms, overwrite=overwrite)
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