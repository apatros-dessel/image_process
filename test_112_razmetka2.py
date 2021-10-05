from script_razmetka_2 import *

corner = r'\\172.21.195.2\thematic\!razmetka\Kanopus\!Kanopus'
categories = [('autumn', 0),
              ('less_snow', 0),
              ('thick_snow', 0),
              ('water', 0),
              ('without_cloud', 0),
              ('mist_cloud_shadow_surface', 0),
              ('blick_bluming_zasvet', 0),
              ('blick_bluming_zasvet', 1),
              # ('strips', 0),
              # ('strips', 1),
              ('add_train', 0),
              ('desert',  0),
              ('surface', 0),
              ('alaska_dekan', 0),
              ]
output_folder = r'e:\test\razmetka_test'

# data = DataFolder(corner)
# for category in categories:
    # data.AlighToMS(category)
    # data.CropPanByMS(category = category, ql = False, cut = False)
# sys.exit()

razmetka = Razmetka(mask_type = 'full', band_type = 'MS', vec_type = 'shp_hand', quicklook_size = None)
for (category, cut) in categories:
    if razmetka.qlsize is not None:
        razmetka.CreateQuicklooks(corner, category, overwrite = False)
    count = razmetka.EnterInput(corner, category, bands = None, use_empty = False, use_cut = cut, burn = None, filter_nodata = True, allow_corner_vector = True)
    print('Обнаружено %i сцен категории %s' % (count, category))
count1 = razmetka.EnterInput(corner, 'strips', bands = None, use_empty = False, use_cut = 0, burn = None, filter_nodata = True, appendix_id = 'strips', allow_corner_vector = True)
count2 = razmetka.EnterInput(corner, 'strips', bands = None, use_empty = False, use_cut = 1, burn = None, filter_nodata = True, appendix_id = 'strips', allow_corner_vector = True)
print('Обнаружено %i сцен категории %s' % (count1 + count2, 'strips'))
razmetka.MakeRazmetka(output_folder, replace = {711: 71, 712: 71, 721: 72, 722: 72, 82:6, 27:17, 811:81, 812:81, 2031:203, 2032:203, 210:71, 211:72, 101:28, 108: 83}, overwrite = False)