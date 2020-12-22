from tools import *

files = folder_paths(r'\\172.21.195.215\thematic\source\ntzomz\__s3_reports',1,'txt')
ids = ['DONE', 'IN_PROC', 'NOT_CHECKED', 'SKIP']
vals = {}
for id in ids:
    vals[id] = {}
    for file in files:
        if re.search(id, file):
            with open(file) as txt:
                vals[id][split3(file)[1]] = len(txt.read().split('\n'))
    print(id, sum(list(vals[id].values())))