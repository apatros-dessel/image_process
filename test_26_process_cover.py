from image_processor import *

# path = r'd:\digital_earth\kanopus_new\krym\KV1_37111_29083_01_KANOPUS_20190331_092700_092901.SCN1.MS_666b82c6286dfde9d29e9f08f738a1fe66fbcf8c'
# proc = process().input(path)

path2xls = r'd:\digital_earth\kanopus_new\vector\krym.xls'
xls_dict = xls_to_dict(path2xls)

# scroll(xls_dict)

vector_cover_in = r'd:\digital_earth\kanopus_new\krym\report_102_2020_116_kv.geojson'
vector_cover_path = r'e:\test\cover_krym.json'
fullpath_list = []

for rowkey in xls_dict:
    path1 = xls_dict[rowkey].get('fullpath', '').encode('utf-8')
    fullpath_list.append(path1)

proc = process().input(copy(fullpath_list))

print(len(proc))

values = proc.get_ids()
for i, val in enumerate(values):
    values[i] = val[:-3]

print(len(values))

geodata.filter_dataset_by_col(vector_cover_in, 'product_id', values, path_out = vector_cover_path)