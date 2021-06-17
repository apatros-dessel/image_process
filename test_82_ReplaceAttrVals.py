from geodata import *

pin = r'e:\rks\razmetka_source\kanopus_full_pms'
attr = 'gridcode'
replace = {203:2033,204:2031,205:2032}

files = folder_paths(pin,1,'shp')

for file in files:
    # print(file)
    vals, attr_fin = GetAttrVals(file, attr)
    vals = flist(vals, int)
    # print(attr_fin)
    if attr_fin is not None:
        if (203 in vals) and ((204 in vals) or (205 in vals)):
            ReplaceAttrVals(file, attr_fin, replace, func=int)
            scroll(GetAttrVals(file, attr), header='NEW:')
        else:
            print('OK: %s' % Name(file))