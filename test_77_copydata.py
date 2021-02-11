from geodata import *

xls_path = r'\\172.21.195.2\thematic\Sadkov_SA\kanopus_dymka\102_2020_1159\report (new_code).xls'
folder_out = r'e:\rks\copy'

xls_dict = xls_to_dict(xls_path)

for path in xls_dict:
    mark = xls_dict[path].get('mark')
    if mark is not None:
        try:
            markid = int(mark)
        except:
            continue
        if markid in range(1,20):
            copydir(split3(path)[0], folder_out)