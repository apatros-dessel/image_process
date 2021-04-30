from geodata import *

raster_in = r'd:\temp\staroselye_dem.tif'
raster_out = r'd:\temp\staroselye_trees.tif'
vector_out = r'd:\temp\staroselye_trees.json'

FindTreesFromDEM(raster_in, raster_out, vector_out, radius=1, min_height=3)