from geodata import *
from image_processor import process, scene

source_folder = r'\\172.21.195.2\thematic\Sadkov_SA\kanopus_dymka\102_2020_1159'
ms_folder = r'\\172.21.195.2\thematic\!razmetka\Kanopus\Kanopus_clouds\MS\img\img_mist'
out_folder = r'd:\rks\kanopus_cloud_test\pan_mist'
out_pms = r'd:\rks\kanopus_cloud_test\pms_mist'
suredir(out_folder)
suredir(out_pms)

def GetMSids(source_folder):
    ids = []
    for name in folder_paths(source_folder,1,'tif'):
        if re.search('MS.+\.tif$', name.lower()):
            ids.append(name[:-4])
    return ids

ms_paths = folder_paths(ms_folder,1,'tif')
ms_ids = flist(ms_paths, lambda x: split3(x)[1])

proc = process().input(source_folder, skip_duplicates=False)

pan_paths = []
pan_ids = []
for ascene in proc.scenes:
    if ascene.meta.type=='PAN':
        # path = ascene.get_raster_path('pan')
        path = folder_paths(ascene.path,1,'tif')[0] or None
        if path:
            pan_paths.append(path)
            pan_ids.append(ascene.meta.id.strip())
        else:
            print('PATH NOT FOUND: %s' % ascene.meta.id)

# scroll(pan_ids)
# scroll(ms_ids)
copypan = deepcopy(pan_ids)
copypan.sort()

for ms, id in zip(ms_paths, ms_ids):
    print(id)
    pan_test = id.replace('.MS','.PAN').strip()
    for pan, pan_id in zip(pan_paths, pan_ids):
        if pan_test==pan_id:
            if RasterMatch(pan, ms) in (1,3):
                endpath = fullpath(out_folder, pan_id, 'tif')
                if not os.path.exists(endpath):
                    shutil.copyfile(pan, endpath)
                    print('COPY: %s' % pan_id)
                else:
                    print('FILE EXISTS: %s' % pan_id)
                pms_id = pan_id.replace('.PAN','.PMS')
                pms = fullpath(out_pms, pms_id, 'tif')
                scroll((endpath, ms, pms))
                cmd_pansharp = r'python py2pci_pansharp.py {} {} {} -d TRUE'.format(endpath, ms, pms)
                os.system(cmd_pansharp)
                if os.path.exists(pms):
                    print('PANSHARPENING SUCCESSFUL: %s' % pms_id)
                else:
                    print('PANSHARPENING ERROR: %s' % pms_id)
            else:
                print('RASTER MISMATCH: %s' % pan_id)
        else:
            # scroll(copypan, lower=id)
            pass
