from geodata import *

pin = r'd:\digital_earth\neuro\object_all_07072020.shp'
field_in = 'path'
field_out = 'path'

din, lin = get_lyr_by_path(pin, 1)
for i, feat in enumerate(lin):
    data = feat.GetField(field_in).decode('utf-8')
    new_data = split3(data)[1]
    feat.SetField(field_out, new_data)
    lin.SetFeature(feat)
    if not i%1000:
        print('%i written %s' % (i/1000, new_data))
ok = input('Write?')
if ok:
    din = None

