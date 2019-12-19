from geodata import raster_data

path = r'd:\rks\minprod\planet_new2\20190910_012717_0f46_3B_AnalyticMS_SR_clip.tif'

x = raster_data(path)
for x, y, z in x.getting((0,1,2)):
    print(z)