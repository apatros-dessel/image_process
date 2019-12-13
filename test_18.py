# merge rasters

from geodata import raster2raster
from image_processor import scene, timecomposite
from geodata import save_to_shp, band_difference, percent
from datetime import datetime as dtime

path2start = [
    r'c:\source\landsat\kirenskoie\LC08_L1TP_131020_20160901_20170321_01_T1\LC08_L1TP_131020_20160901_20170321_01_T1_B4.TIF',
    r'c:\source\landsat\kirenskoie\LC08_L1TP_131020_20160901_20170321_01_T1\LC08_L1TP_131020_20160901_20170321_01_T1_B3.TIF',
    r'c:\source\landsat\kirenskoie\LC08_L1TP_131020_20160901_20170321_01_T1\LC08_L1TP_131020_20160901_20170321_01_T1_B2.TIF',
]
path2target = r'c:\source\landsat\kirenskoie\LC08_L1TP_131020_20160901_20170321_01_T1\LC08_L1TP_131020_20160901_20170321_01_T1_B4.TIF'
path2export = r'c:\sadkov\temp\timecomp.tif'
path2dif = r'c:\sadkov\temp\dif.tif'
path2newshp = r'c:\sadkov\temp\change.shp'
bands = [1,1,1]

path_new = r'c:\source\landsat\kirenskoie\LC08_L1TP_132019_20190715_20190720_01_T1\LC08_L1TP_132019_20190715_20190720_01_T1_MTL.txt'
path_old = r'c:\source\landsat\kirenskoie\LC08_L1TP_132019_20180813_20180828_01_T1\LC08_L1TP_132019_20180813_20180828_01_T1_MTL.txt'
path2shp = r'C:/sadkov/forest/kirenskoe/aoi/kirenskoe_utm48.shp'

t = dtime.now()

#raster2raster(path2start, path2target, path2export, bands)
scenes = [scene(path_new), scene(path_old)]
for scene in scenes:
    scene.clip(path2shp)
# s.composite(['red', 'green', 'blue'], r'C:\sadkov\temp\comp2.tif')
# timecomposite(scenes, ['nir', 'nir', 'green'], [0, 1, 0], path2export, exclude_nodata = True)
# band_difference(path2export, path2dif, 1, 2)
# percent(path2export, path2dif, 1, 2)
save_to_shp(path2dif, path2newshp, classify_table=[[None, -10, 0], [10, None, 1]], export_values=[0, 1])

print(dtime.now() - t)