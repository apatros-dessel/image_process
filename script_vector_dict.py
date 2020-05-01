
from geodata import *
from datetime import datetime

t = datetime.now()
path2json = r'c:\sadkov\toropez\image_test\temp_json.json'
json = ogr.Open(path2json)
lyr = json.GetLayer()
lyr_dict = layer_column_dict(lyr, geom_col_name='Geometry', lyr_defn_name='Layer_Defn', field_defn_col_name='Field_Defn', columns_as_arrays=True)
scroll(lyr_dict)
print(datetime.now() - t)

# print(lyr_dict.get('Geometry').dtype)