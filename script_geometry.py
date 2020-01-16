from image_processor import *
# path2shp2 = r'c:\sadkov\toropez\image_test\full\Mosaic_20190405_1042_DEFLATE.shp'
# path2shp1 = r'c:\sadkov\toropez\image_test\full\Mosaic_20190405_1044_DEFLATE.shp'
from datetime import datetime

path2shape_list = [
    r'c:\sadkov\toropez\planet\20190516\2367219_3665010_2019-05-16_1011\2367219_3665010_2019-05-16_1011_metadata.json',
    r'c:\sadkov\toropez\planet\20190516\2367219_3665110_2019-05-16_1011\2367219_3665110_2019-05-16_1011_metadata.json',
    r'c:\sadkov\toropez\planet\20190516\2367219_3665111_2019-05-16_1011\2367219_3665111_2019-05-16_1011_metadata.json',
]

path2export = r'c:\sadkov\toropez\image_test\test_json.json'

proc = process()
proc.input(r'c:\sadkov\toropez\planet', imsys_list=['PLN'])
cover_paths = proc.get_cover_paths()

scroll(cover_paths)
t = datetime.now()
# geodata.IntersectCovers(path2shp1, path2shp2, r'c:\sadkov\toropez\image_test\test.shp')
geodata.JoinShapesByAttributes(cover_paths.values(), r'c:\sadkov\toropez\image_test\temp_json.json', ['id'], geom_rule=1, attr_rule=0, )
'''
temp_ds = geodata.ogr.Open(r'c:\sadkov\toropez\image_test\temp_json.json', 1)
temp_lyr = temp_ds.GetLayer()
field_defn = geodata.ogr.FieldDefn('date', geodata.ogr.OFTString)
field_defn.SetWidth(10)
temp_lyr.CreateField(field_defn)

temp_ds = None
temp_ds = geodata.ogr.Open(r'c:\sadkov\toropez\image_test\temp_json.json', 1)
temp_lyr = temp_ds.GetLayer()

for feat in temp_lyr:
    feat.GetDefnRef().AddFieldDefn(field_defn)
    feat.SetField('date', feat.GetFieldAsString(feat.GetFieldIndex('aquired')))

temp_ds = None
'''
geodata.JoinShapesByAttributes([r'c:\sadkov\toropez\image_test\temp_json.json'], path2export, ['satellite_id', 'strip_id'], geom_rule=1, attr_rule=0, )
print(datetime.now()-t)

'''
js = geodata.ogr.Open(path2export, 1)
lyr = js.GetLayer()
for i, feat in enumerate(lyr):
    feat.SetFID(i)
    # print(feat.GetFID())
js = None
'''
