from geodata import *

ids = [
    'KV1_38765_30109_00_KANOPUS_20190718_080631_080722.SCN10.PMS.L2',
    'KV1_38765_30109_00_KANOPUS_20190718_080631_080722.SCN11.PMS.L2',
    'KV1_38765_30109_00_KANOPUS_20190718_080631_080722.SCN12.PMS.L2',
    'KV1_38765_30109_00_KANOPUS_20190718_080631_080722.SCN13.PMS.L2',
    'KV1_38765_30109_00_KANOPUS_20190718_080631_080722.SCN9.PMS.L2'
]

path_cover = r'd:\terratech\covers\102_2020_180_Samara_fullcover.json'
path_out = r'd:\terratech\covers\test'

suredir(path_out)

for pms_id in ids:
    get_pms_json_from_ms(path_cover, fullpath(path_out, pms_id, 'json'), pms_id)
    json_fix_datetime(fullpath(path_out, pms_id, 'json'))