from geodata import *

vec_list = folder_paths(r'\\172.21.195.2\thematic\Sadkov_SA\pkk',1,'shp')
attr = 'cadn'
vals = ['35:11:0000000:113','75:14:400303:250','37:10:010311:374','50:03:0040280:178','50:03:0040280:25','50:03:0040280:2099','50:03:0040280:2074','63:26:0000000:554']
pout = r'\\172.21.195.2\thematic\Sadkov_SA\pkk\export.json'

SelectFromVectorByAttribute(vec_list, attr, vals, pout, proj=get_srs(4326), single = True)