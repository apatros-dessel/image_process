from geodata import *

pin = r'\\tt-pc-10-quadro\FTP_Share14TB\Рослесинфорг\AIRBUS\Roslesinforg_14sept2020_AOI1_SO20194111-10-01_DS_PHR1A_202008170615476_FR1_PX_E094N68_0321_01654\5326237101\IMG_PHR1A_PMS_001\DIM_PHR1A_PMS_202008170615476_SEN_5326237101.XML'
pout = r'\\tt-pc-10-quadro\FTP_Share14TB\Рослесинфорг\AIRBUS\Roslesinforg_14sept2020_AOI1_SO20194111-10-01_DS_PHR1A_202008170615476_FR1_PX_E094N68_0321_01654\5326237101\IMG_PHR1A_PMS_001\cover.json'

def MultipolygonFromMeta(metapath, srs = None, coord_start = '<Dataset_Extent>', coord_fin = '</Dataset_Extent>', vertex_start = '<Vertex>', vertex_fin = '</Vertex>'):
    lines_ = flist(open(metapath).read().split('\n'), lambda x: x.strip())
    coord_data = find_parts(lines_, coord_start, coord_fin)[0]
    vertices = find_parts(coord_data, vertex_start, vertex_fin)
    wkt = 'MULTIPOLYGON ((('
    for point in vertices:
        x = re.search('\d+\.\d+', point[0]).group()
        y = re.search('\d+\.\d+', point[1]).group()
        wkt += '%s %s,' % (x, y)
    wkt += '%s %s)))' % (re.search('\d+\.\d+', vertices[0][0]).group(), re.search('\d+\.\d+', vertices[0][1]).group())
    geom = ogr.CreateGeometryFromWkt(wkt, srs)
    return geom

srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

geom = MultipolygonFromMeta(pin, srs)

dout = json(pout, editable=True)
lyr = dout.GetLayer()
feat = ogr.Feature(lyr.GetLayerDefn())
feat.SetGeometry(geom)
lyr.CreateFeature(feat)
dout = None