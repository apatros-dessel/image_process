from geodata import *
import shutil

path_orig = r'e:\planet_rgb'
path_export = r'd:\export\planet\tver'

orig_files = folder_paths(path_orig, 1, 'tif')
folders, files = folder_paths(path_export)

for i, folder in enumerate(folders):
    base, end = os.path.split(folder)
    json_path = fullpath(folder, end, 'json')
    if not os.path.exists(json_path):
        print('%i No json found in %s' % (i, folder))
        continue
    srname = '%s_SR.tif' % end
    origname = '%s.tif' % end
    fin = False
    for orig_path in orig_files:
        if srname in orig_path:
            shutil.copyfile(orig_path, fullpath(folder, end, 'tif'))
            print('%i SR written: %s' % (i, folder))
            fin = True
            break
    if fin:
        continue
    for orig_path in orig_files:
        if origname in orig_path:
            shutil.copyfile(orig_path, fullpath(folder, end, 'RGB.tif'))
            print('%i RGB written %s' % (i, folder))
            fin = True
            break
    if fin:
        continue
    print('%i File not found: %s' % (i, folder))
