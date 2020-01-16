from image_processor import *
# path2shp2 = r'c:\sadkov\toropez\image_test\full\Mosaic_20190405_1042_DEFLATE.shp'
# path2shp1 = r'c:\sadkov\toropez\image_test\full\Mosaic_20190405_1044_DEFLATE.shp'

path2shape_list = [
    r'c:\sadkov\toropez\planet\20190516\2367219_3665010_2019-05-16_1011\2367219_3665010_2019-05-16_1011_metadata.json',
    r'c:\sadkov\toropez\planet\20190516\2367219_3665110_2019-05-16_1011\2367219_3665110_2019-05-16_1011_metadata.json',
    r'c:\sadkov\toropez\planet\20190516\2367219_3665111_2019-05-16_1011\2367219_3665111_2019-05-16_1011_metadata.json',
]

path2export = r'c:\sadkov\toropez\image_test\test_json.json'

# geodata.IntersectCovers(path2shp1, path2shp2, r'c:\sadkov\toropez\image_test\test.shp')
geodata.JoinShapesByAttribute(path2shape_list, path2export, geom_rule=2, attr_rule=2, attribute='anomalous_pixels')

'''
js = geodata.ogr.Open(path2export, 1)
lyr = js.GetLayer()
for i, feat in enumerate(lyr):
    feat.SetFID(i)
    # print(feat.GetFID())
js = None
'''
