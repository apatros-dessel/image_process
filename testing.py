from image_process import *

proc = process()
#proc.image_system = 'Sentinel'
proc.return_bands = True
proc.filter_clouds = True
proc.ath_corr_method = 'DOS1'
proc.input(r'E:\data')
s = proc[0]
s.mask('QUALITY', 2720, True, 'Cloud')
s.ndwi('DOS1')
s.save_to_shp('NDWI_DOS1', r'E:\data\test.shp', mask_list=['Cloud'], classify_param={'borders': [0]})

#proc.input(r'C:\sadkov\sentinel\new\S2A_MSIL1C_20180622T080611_N0206_R078_T37TGN_20180622T092729.SAFE')
proc.output_path = r'E:\data'
#ss = proc[1]
#proc.input('C:\\sadkov\\lsat8')
#proc.input('C:\\sadkov\\sentinel')
#proc[0].ndwi('None')
#proc.run('ndwi')

#proc.composite(22, interpol_method=gdal.GRA_Average)
'''

s=proc[3]
t=proc[22]
s.mask('QUALITY', 2720, True, 'Cloud')
t.merge_band('4', s.mask_dataset('Cloud'), 'Cloud_old', method=gdal.GRA_Average)
t.mask('Cloud_old', 1)
os.chdir(proc.output_path)
t.save(4, 'test.tif', ['Cloud_old'])


t.mask_dataset('Cloud_old', 'exp')
t.save('exp', 'test.tif')

#s = proc[0]
lsat = proc[4]
lsat2 = proc[6]
#sent = proc[21]
#sent.merge_band('8', lsat['5'], data_newid='merge', method=gdal.GRA_Max)
#sent.mask('merge')

interpol_method = gdal.GRA_Average
lsat.merge_band('4', lsat.radiance(4), 'merge', t_band_num=1, method=interpol_method)
lsat.merge_band('4', lsat2.radiance(4), 'merge', t_band_num=2, method=interpol_method)
lsat.merge_band('4', lsat.radiance(3), 'merge', t_band_num=3, method=interpol_method)
lsat.save('merge', 'c:\\sadkov\\test.tif')

lsat.mask('QUALITY', 2720, True, 'Cloud')
lsat.merge_band('4', lsat.mask_dataset('Cloud'), 'lsat_cloud', method=gdal.GRA_Min)
lsat.mask('lsat_cloud', include='True')
vector_path = sent.meta_call('MASK_FILENAME', check={'type': 'MSK_CLOUDS'}, mtd=True)
vector_path = '{}\\{}'.format(sent.folder, vector_path)
if os.path.exists(vector_path):
    sent.vector_mask(vector_path, 'Cloud', data_id='3')
else:
    print('Vector mask not found: {}'.format(vector_path))

#s.save_to_shp('QUALITY', 'c:\\sadkov\\test.shp')
#s.ndwi('DOS1')


#s.save('NDWI_DOS1', 'C:\\sadkov\\test_2.tif', ['3', '5', 'Cloud'])
#proc.ndvi_procedure(8)
#proc.run('ndwi')
'''
