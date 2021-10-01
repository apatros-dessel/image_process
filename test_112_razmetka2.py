from script_razmetka_2 import *

corner = r'\\172.21.195.2\thematic\!razmetka\Resurs_geoton\!Resurs_Geoton'
categories = ['without_cloud', 'water']
output_folder = r'e:\test\razmetka_test'

razmetka = Razmetka(mask_type = 'full', band_type = 'MS', vec_type = 'shp_hand', quicklook_size = 30)
for category in categories:
    if razmetka.qlsize is not None:
        razmetka.CreateQuicklooks(corner, category, overwrite = False)
    count = razmetka.EnterInput(corner, category, bands = None, use_empty = False, use_cut = False, burn = None, filter_nodata = True, allow_corner_vector = True)
    print('Обнаружено %i сцен категории %s' % (count, category))
if razmetka.qlsize is not None:
    razmetka.CreateQuicklooks(corner, 'full_cloud', overwrite = False)
count = razmetka.EnterInput(corner, 'full_cloud', bands = None, use_empty = True, use_cut = False, burn = 201, filter_nodata = True, allow_corner_vector = True)
print('Обнаружено %i сцен категории %s' % (count, 'full_cloud'))
# scroll(razmetka.input, counts=True)
razmetka.MakeRazmetka(output_folder, replace = {811:81, 812:82}, overwrite = False)