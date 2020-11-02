from image_processor import *

path_in = r'd:\terratech\Krym_buildings_5masks'
path_out = r'd:\terratech\razmetka'

path_set = fullpath(path_out, 'set007__20200416__Krym_houses')

path_images = fullpath(path_set, 'images\\resurs')
path_masks = fullpath(path_set, 'masks\\houses\\resurs')

def kanopus_index(filename):
    satid, loc1, sentnum, date, num1, ending = undersplit = filename.split('_')
    dotsplit = ending.split('.')
    scn = dotsplit[1]
    # type = dotsplit[2]
    # lvl = dotsplit[3]
    # ext = dotsplit[-1]
    scn_num = scn.replace('SCN', '')
    indexname = '{}-{}-{}{}{}-L2'.format(satid, date, loc1, sentnum, scn_num)
    return indexname

suredir(path_images)
suredir(path_masks)

folders_list = folder_paths(path_in)[0]

for folder in folders_list:
    raster_paths = folder_paths(folder, True, 'tif')
    for raster_path in raster_paths:
        if not 'rgb' in raster_path.lower():
            break
    raster_name = os.path.basename(raster_path)
    shp_path = folder_paths(folder, True, 'shp')[0]
    index = kanopus_index(raster_name[4:-4])
    shutil.copyfile(raster_path, fullpath(path_images, 'IM4-%s.tif' % index))
    geodata.RasterizeVector(shp_path, raster_path,
                    fullpath(path_masks, 'MBD-%s.tif' % index),
                    value_colname='gridcode',
                    compress='DEFLATE', overwrite=False)
