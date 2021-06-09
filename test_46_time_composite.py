from geodata import *

raster_old = r'e:\rks\kantest\Kanopus_surface\PMS\img\img_check\KV1_32721_25999_01_KANOPUS_20180615_043415_043537.SCN09.PMS.L2.tif'
raster_new = r'e:\rks\kantest\Kanopus_surface\PMS\img\img_check\KV3_12769_10030_01_KANOPUS_20200522_040148_040418.SCN09.PMS.L2.tif'
export_path = r'e:\rks\kantest\Kanopus_surface\PMS\img\img_check\KV1_32721_25999_01_KANOPUS_20180615_043415_043537.SCN09.PMS.L2__KV3_12769_10030_01_KANOPUS_20200522_040148_040418.SCN09.PMS.L2__3CH.tif'

path2raster_list = [
    (raster_old,1),
    (raster_old,2),
    (raster_old,3),
    (raster_old,4),
    (raster_new,1),
    (raster_new,2),
    (raster_new,3),
    (raster_new,4),
]

t = datetime.now()
temp_old_red = tempname('tif')
ds(temp_old_red, copypath=raster_old, options={'bandnum':1, 'compress':'DEFLATE'})
StackBand((raster_old,1), (temp_old_red,1), tile_size=10000)
print('Old red extracted for {}'.format(datetime.now() - t))

t = datetime.now()
temp_old_red_2 = tempname('tif')
Mosaic([temp_old_red], temp_old_red_2, band_num=1, band_order=None, copyraster=raster_new, options={'compress':'DEFLATE'})
print('Old red reprojected for {}'.format(datetime.now() - t))
suredir(os.path.dirname(export_path))

t = datetime.now()
ds(export_path, copypath=raster_new, options={'bandnum':3, 'compress':'DEFLATE'})
StackBand((raster_new, 1), (export_path, 1), tile_size=10000)
StackBand((temp_old_red_2, 1), (export_path, 2), tile_size=10000)
StackBand((raster_new, 2), (export_path, 3), tile_size=10000)
SetNoData(export_path, 0)
print('Composite made for {}'.format(datetime.now() - t))

for p in (temp_old_red, temp_old_red_2):
    os.remove(p)