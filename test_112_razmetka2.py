from script_razmetka_2 import *

corner = r'\\172.21.195.2\thematic\!razmetka\Kanopus\!Kanopus'
categories = [('autumn', 0),
              ('less_snow', 0),
              ('thick_snow', 0),
              ('water', 0),
              ('without_cloud', 0),
              ('mist_cloud_shadow_surface', 0),
              # ('blick_bluming_zasvet', 0),
              # ('blick_bluming_zasvet', 1),
              # ('strips', 0),
              # ('strips', 1),
              ('add_train', 0),
              ('desert',  0),
              ('surface', 0),
              ('alaska_dekan', 0),
              ]

bands_params = [
    ('red', [1]),
    ('green', [2]),
    ('blue', [3]),
    ('nir', [4]),
]
i = 154

output_folder = r'e:\rks\razmetka\set999__20211012__kanopus_ms_all_bands__red_12bit'
razmetka = Razmetka(mask_type = 'full', band_type = 'MS', vec_type = 'shp_hand', quicklook_size = None)
for (category, cut) in categories:
    count = razmetka.EnterInput(corner, category, bands = None, use_empty = False, use_cut = cut, burn = None, filter_nodata = True, by_bands = 1, appendix_id = '__12_bit', allow_corner_vector = True)
    print('Обнаружено %i сцен категории %s' % (count, category))
for bandid, bands in bands_params:
    for (category, cut) in categories:
        check_count = razmetka.EnterCheck(corner, category, bands = bands, use_cut = cut, by_bands = False, appendix_id = bandid + '__12_bit')
        # print('Обнаружено %i контрольных сцен категории %s' % (check_count, category))
# scroll(razmetka.input, counts=1)
# sys.exit()
for filter_mark in ['red']:#, 'green', 'blue', 'nir']:
    i += 1
    output_folder = r'e:\rks\razmetka\set%i__20211012__kanopus_ms_all_bands_%s__12bit' % (i, filter_mark)
    razmetka.MakeRazmetka(output_folder, del_codes = [232], cut_bits_limit = True, min_bits_limit = 8, overwrite = False, filter_mark = filter_mark, control_lim = 6,
                          replace = {711: 71, 712: 71, 721: 72, 722: 72, 82:6, 27:17, 811:81, 812:81, 2031:0, 2032:0, 203:0, 210:71, 211:72, 101:28, 108: 83, 55:54, 541:54, 542:54, 220:0})


sys.exit()

for app, bands in bands_params:
    i += 1
    output_folder = r'e:\rks\razmetka\set%i__20211008__kanopus_ms_all_bands_%s__12bit' % (i, app)
    appendix_id = app + '__12bit'

    # data = DataFolder(corner)
    # for category in categories:
        # data.AlighToMS(category)
        # data.CropPanByMS(category = category, ql = False, cut = False)
    # sys.exit()

    razmetka = Razmetka(mask_type = 'full', band_type = 'MS', vec_type = 'shp_hand', quicklook_size = None)
    for (category, cut) in categories:
        if razmetka.qlsize is not None:
            razmetka.CreateQuicklooks(corner, category, overwrite = False)
            if cut:
                razmetka.CutQuicklooks(corner, category, overwrite = False)
        count = razmetka.EnterInput(corner, category, bands = bands, use_empty = False, use_cut = cut, burn = None, filter_nodata = True, appendix_id = appendix_id, allow_corner_vector = True)
        print('Обнаружено %i сцен категории %s' % (count, category))
        if razmetka.qlsize is not None:
            razmetka.CreateQuicklooks(corner, category, type = 'img_check', overwrite = False)
            if cut:
                razmetka.CutQuicklooks(corner, category, type = 'img_check', overwrite = False)
        check_count = razmetka.EnterCheck(corner, category, bands = bands, use_cut = cut, by_bands = False, appendix_id = appendix_id)
        print('Обнаружено %i контрольных сцен категории %s' % (count, category))
    if razmetka.qlsize is not None:
        razmetka.CreateQuicklooks(corner, 'strips', overwrite = False)
        razmetka.CutQuicklooks(corner, 'strips', overwrite=False)
    count1 = razmetka.EnterInput(corner, 'strips', bands = bands, use_empty = False, use_cut = 0, burn = None, filter_nodata = True, appendix_id = 'strips_' + appendix_id, allow_corner_vector = True)
    count2 = razmetka.EnterInput(corner, 'strips', bands = bands, use_empty = False, use_cut = 1, burn = None, filter_nodata = True, appendix_id = 'strips_' + appendix_id, allow_corner_vector = True)
    print('Обнаружено %i сцен категории %s' % (count1 + count2, 'strips'))
    if razmetka.qlsize is not None:
        razmetka.CreateQuicklooks(corner, 'strips', type='img_check', overwrite=False)
        razmetka.CutQuicklooks(corner, 'strips', type='img_check', overwrite=False)
    check_count = razmetka.EnterCheck(corner, 'strips', bands=bands, use_cut=cut, by_bands=False, appendix_id='red_strips')
    print('Обнаружено %i контрольных сцен категории %s' % (count, category))
    razmetka.MakeRazmetka(output_folder,
                          replace = {711: 71, 712: 71, 721: 72, 722: 72, 82:6, 27:17, 811:81, 812:81, 2031:203, 2032:203, 210:71, 211:72, 101:28, 108: 83, 55:54, 541:54, 542:54},
                          del_codes = [232], cut_bits_limit = True, overwrite = False)