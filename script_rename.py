from tools import *

path = r'e:\rks\resurs_granules_new\RP1_28583_05_GEOTON_20180804_081628_081701.SCN3.PMS.L2.GRN36036032'

def rename(n):
    for str_ in ('.QL', '.RGB', '.IMG'):
        if re.search(str_, n):
            if not n.endswith(str_):
                new = n.replace(str_, '') + str_
                return new
    return n

files = folder_paths(path, 1)

for file in files:
    f,n,e = split3(file)
    new = rename(n)
    if n!=new:
        os.rename(file, fullpath(f,new,e))

# scroll(files)