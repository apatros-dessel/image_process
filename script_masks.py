from geodata import *
from shutil import copyfile

def kanopus_index(file_id):
    satid, loc1, loc2, sentnum, kanopus, date, num1, ending = undersplit = file_id.split('_')
    dotsplit = ending.split('.')
    scn_num = dotsplit[1].replace('SCN', '')
    indexname = 'IM4-{}-{}-{}{}{}-L2'.format(satid, date, loc1, loc2, scn_num)
    return indexname

def new_names_for_source(raster_list, vector_list):

    def fileids(path_list, ext=True):
        fileid_list = []
        for path in path_list:
            basename = os.path.basename(path)
            if ext:
                fileid_list.append(basename)
            else:
                fileid_list.append(os.path.splitext(basename)[0])
        return fileid_list

    def list_counter(list_):
        counts = {}
        for val_ in list_:
            counts[val_] = counts.get(val_, 0) + 1
        return counts

    r_ids = fileids(raster_list, False)
    v_ids = fileids(vector_list, False)

    r_count = list_counter(r_ids)
    v_count = list_counter(v_ids)

    v_lost = []
    r_lost = []

    for r_id in r_count:
        if r_count[r_id] == 1:
            v_id_c = v_count.get(r_id)
            if v_id_c == 1:
                continue
            elif v_ids is None:
                v_lost.append(r_id)




raster_index_col_name = 'gridcode'
compression = 'DEFLATE'
overwrite_existing_files = False

path_raster = r'g:\rks\digital_earth\processed\kanopus\Tver\ms'
path_vector = r'g:\rks\digital_earth\data_2_razmetka\20200427\water\shp\Tver'
path_out = r'd:\terratech\razmetka\set013__20200428__water_kanopus_ms'

raster_list = folder_paths(path_raster,1,'tif')
vector_list = folder_paths(path_vector,1,'shp')
path_im4 = fullpath(path_out, r'images\kanopus')
path_mask = fullpath(path_out, r'masks\buildings\kanopus')

suredir(path_im4)
suredir(path_mask)

# scroll(raster_list)
# scroll(vector_list)

i = 1
for filepath in raster_list:
    file = os.path.split(filepath)[1]
    file_id = os.path.splitext(file)[0]
    kan_nameIM4 = kanopus_index(file_id)#.replace('.MS', '.PMS')
    kan_nameMSK = kan_nameIM4.replace('IM4', 'MWT')
    for shp_path in vector_list:
        shp = os.path.split(shp_path)[1]
        shp_id = os.path.splitext(shp)[0].replace('.MS', '.MS.L2')
        if file_id == shp_id:

            # kan_pathMSK = fullpath(path_mask, kan_nameMSK, 'tif')
            # if os.path.exists(kan_nameMSK):
                # break

            kan_pathIM4 = fullpath(path_im4, kan_nameIM4, 'tif')

            if os.path.exists(kan_pathIM4):
                i_val = 1
                im_path_new = kan_pathIM4.replace('-L2', '!%s-L2' % stringoflen(i_val, 3, filler='0', left=True))
                while os.path.exists(im_path_new):
                    i_val += 1
                    im_path_new = kan_pathIM4.replace('-L2', '!%s-L2' % stringoflen(i_val, 3, filler = '0', left = True))
                kan_pathIM4 = im_path_new
                kan_nameMSK = os.path.basename(kan_pathIM4).replace('IM4', 'MWT')[:-4]

            kan_pathMSK = fullpath(path_mask, kan_nameMSK, 'tif')

            # Change gridcode value

            shp_ds, shp_lyr = get_lyr_by_path(shp_path, 1)
            for feat in shp_lyr:
                # feat = shp_lyr.GetNextFeature()
                feat.SetField(raster_index_col_name, 9)
                shp_lyr.SetFeature(feat)
            shp_ds = None


            RasterizeVector(shp_path, filepath, kan_pathMSK,
                                    value_colname=raster_index_col_name,
                                    filter_nodata=True,
                                    compress=compression,
                                    overwrite=overwrite_existing_files)
            copyfile(filepath, kan_pathIM4)
            print('%i Mask written: %s' % (i, file_id))
            i +=1
            break
    # print('%i Error writing mask: %s' % (i+1, kan_nameIM4))

# scroll(filepath_list)