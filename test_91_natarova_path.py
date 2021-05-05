from tools import *

xls_check = r'\\172.21.195.2\thematic\!SPRAVKA\S3\16\report_kv_water.xls'
xls_paths = r'\\172.21.195.2\thematic\!SPRAVKA\S3\16\16.xls'
txt_path = r'\\172.21.195.2\thematic\!SPRAVKA\S3\16\report_kv_water.txt'
marks = ['997']
mount = 'y:/'

check = xls_to_dict(xls_check)
paths = xls_to_dict(xls_paths)
path_list = []

for path0 in check:
    # scroll(check[path0])
    mark = str(int(check[path0].get('mark')))
    # print(mark)
    if mark:
        if FindAny(mark, marks):
            id = check[path0].get('id')
            if id in paths:
                path1 = paths[id].get('Path')
                if path1:
                    path_fin = mount + path1.split('natarova')[-1]
                    print(path_fin)
                    path_list.append(path_fin)

with open(txt_path, 'w') as txt:
    txt.write('\n'.join(path_list))