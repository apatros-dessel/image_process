from geodata import *

xls = r'e:\rks\razmetka\set050__20210304__kanopus_mist_cloud_shadow_surface\quicklook\30\report_2021-03-04_11-30-05.481744.xls'

xls_dict = xls_to_dict(xls)
keys = list(xls_dict.keys())
files = folder_paths(r'e:\rks\razmetka\set050__20210304__kanopus_mist_cloud_shadow_surface',1,'tif')

for key in keys:
    vals = xls_dict[key]
    msk_vals = vals['msk_values'].split(' ')
    for i in ('203','2031','2032','2033'):
        if i in msk_vals:
            xls_dict.pop(key)
            baseid = '-'.join(key.split('-')[1:])
            for file in files:
                if baseid in file:
                    delete(file)
            break

# scroll(flist(list(xls_dict.values()), lambda x: [x['msk_values'].split(' ')]), lower=len(xls_dict))
dict_to_xls(r'e:\rks\razmetka\set050__20210304__kanopus_mist_cloud_shadow_surface\quicklook\30\report_2021-03-10.xls', xls_dict)