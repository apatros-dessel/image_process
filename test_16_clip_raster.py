# Clips raster with shapefile

from geodata import clip_raster
path2raster = r'c:\sadkov\forest\kirenskoe\composite\lsat_132019_2019-2018_nRoRnG.tif'
path2vector = r'c:\sadkov\forest\kirenskoe\aoi\kirenskoe.shp'
path2export = r'C:\sadkov\temp\clip.tif'
clip_raster(path2raster, path2vector, path2export)