from geodata import *

pin = r'e:\rks\razmetka_source\kanopus_mist_cloud_shadow_surface\shp_hand_mist_cloud_shadow_surface'
attr = 'gridcode'
replace = {203:2033,204:2031,205:2032}

files = folder_paths(pin,1,'shp')

for file in files:
    print(file)
    vals = flist(GetAttrVals(file, attr), int)
    print(vals)
    if (203 in vals) and ((204 in vals) or (205 in vals)):
        ReplaceAttrVals(file, attr, replace, func=int)
        # scroll(GetAttrVals(file, attr), header='NEW:')