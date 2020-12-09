from geodata import *

corner = r'\\172.21.195.215\thematic\products\db_etalons'

folders = folder_paths(corner)[0]
for dir_in in folders:
    mask_dir = fullpath(dir_in, 'masks')
    if os.path.exists(mask_dir):
        dir0, imsys = os.path.split(dir_in)
        dir0, type = os.path.split(dir0)
        print('Start %s-%s' % (type, imsys))
        shp_dir = fullpath(dir_in, 'shp')
        suredir(shp_dir)
        old_shps = folder_paths(shp_dir,1,'shp')
        if len(old_shps)==0:
            old_masks = folder_paths(mask_dir,'tif')
            for i, mask in enumerate(old_masks):
                name = split3(mask)[1]
                VectorizeBand((mask, 1), fullpath(shp_dir,name,'shp'), classify_table=None, index_id='ID', overwrite=False)
                print('%i from %i: %s' % (i+1, len(old_masks), name))
    else:
        # print('Mask dir not found: %s' % mask_dir)
        pass

# pin = r'd:\temp\MCHD8__S2A-20190802-T46VEL-L2A__S2A-20200702-T46VEL-L2A.tif'
# pout = r'd:\temp\MCHD8__S2A-20190802-T46VEL-L2A__S2A-20200702-T46VEL-L2A.shp'

# VectorizeBand((pin, 1), pout, classify_table=None, index_id = 'ID', overwrite = False)