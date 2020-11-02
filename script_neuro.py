from geodata import *

path2raster = r'D:/Krym/!fin/rgb/RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2_obrez_ref.RGB.tif'
path2cover = r'D:/Krym/!fin/mask.geojson'
path2attr = r'D:/export/resursp/krym/RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2_obrez/RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2_obrez.json'
path2cover_fin = r'D:/Krym/!fin/RP1_28828_05_GEOTON_20180820_081207_081219.SCN2.PMS.L2_obrez_ref.json'

# RasterDataMask(path2raster, path2cover, use_nodata = True, enforce_nodata = 0, alpha=None, overwrite = True)
change_single_geom(path2attr, path2cover, path2cover_fin)