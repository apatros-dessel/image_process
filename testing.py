from image_process import *

proc = process()
#proc.image_system = 'Sentinel'
proc.return_bands = True
proc.filter_clouds = True
#proc.ath_corr_method = 'DOS1'
proc.input_path = r'C:\sadkov\lsat8\test\LC08_L1TP_173027_20180727_20180731_01_T1'
#proc.input_path = r'C:\sadkov\sentinel\new\S2A_MSIL1C_20180622T080611_N0206_R078_T37TGN_20180622T092729.SAFE'
proc.output_path = r'C:\sadkov'
proc.input('C:\\sadkov\\lsat8')
proc.input('C:\\sadkov\\sentinel')
proc.composite(22)

'''
#s = proc[0]
lsat = proc[4]
sent = proc[21]
#sent.merge_band('8', lsat['5'], data_newid='merge', method=gdal.GRA_Max)
#sent.mask('merge')

interpol_method = gdal.GRA_CubicSpline
sent.merge_band('4', sent['4'], 'merge', t_band_num=1, method=interpol_method)
sent.merge_band('4', lsat['4'], 'merge', t_band_num=2, method=interpol_method)
sent.merge_band('4', sent['3'], 'merge', t_band_num=3, method=interpol_method)

lsat.mask('QUALITY', 2720, True, 'Cloud')
sent.merge_band('4', lsat.mask_dataset('Cloud'), 'lsat_cloud', method=gdal.GRA_Min)
sent.mask('lsat_cloud', include='True')
vector_path = sent.meta_call('MASK_FILENAME', check={'type': 'MSK_CLOUDS'}, mtd=True)
vector_path = '{}\\{}'.format(sent.folder, vector_path)
if os.path.exists(vector_path):
    sent.vector_mask(vector_path, 'Cloud', data_id='3')
else:
    print('Vector mask not found: {}'.format(vector_path))
sent.save('merge', 'c:\\sadkov\\test_0.tif', ['Cloud'])
#s.save_to_shp('QUALITY', 'c:\\sadkov\\test.shp')
#s.ndwi('DOS1')


#s.save('NDWI_DOS1', 'C:\\sadkov\\test_2.tif', ['3', '5', 'Cloud'])
#proc.ndvi_procedure(8)
#proc.run('ndwi')
'''