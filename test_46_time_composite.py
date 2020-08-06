from geodata import *

raster_old = r'e:\rks\mosaics\June\cut3\Ostashkovskoe2020_june_cut3.tif'
raster_new = r'e:\rks\mosaics\July\cut1\Ostashkovskoe_July_cut1_mos.tif'
export_path = r'e:\rks\mosaics\Planet_mosaic_composite_June3-July1_manual_slow.tif'

path2raster_list = [
    (raster_new, 1),
    (raster_old,1),
    (raster_new,2),
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

t = datetime.now()
ds(export_path, copypath=raster_new, options={'bandnum':3, 'compress':'DEFLATE'})
StackBand((raster_new, 1), (export_path, 1), tile_size=10000)
StackBand((temp_old_red_2, 1), (export_path, 2), tile_size=10000)
StackBand((raster_new, 2), (export_path, 3), tile_size=10000)
SetNoData(export_path, 0)
print('Composite made for {}'.format(datetime.now() - t))

for p in (temp_old_red, temp_old_red_2):
    os.remove(p)