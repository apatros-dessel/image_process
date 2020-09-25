from geodata import *

raster_old = r'D:/digital_earth/planet_20200920/2019-08-02_v2/Madashenskoe_20190802_rgb_v2.tif'
raster_new = r'D:/digital_earth/planet_20200920/2019-08-08_v2/Madashenskoe_20190808_rgb_v2.tif'
export_path = r'd:\digital_earth\planet_20200920\Madashenskoe_2019aug02-08_rgb_v2.tif'

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