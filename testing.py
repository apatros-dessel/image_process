
# MAKES A VECTOR LAYER OF WATER FROM SENTINEL OR LANDSAT IMAGE USING NDWI INDEX

from image_process import *

proc = process()


'''
os.chdir(r'C:\sadkov\tulun\')

band_new = np.zeros(data_array[0].shape).astype(np.float32)
for id in range(4):
    band = data_array[id].astype(np.float32)
    #min_ = np.min(band); max_ = np.max(band)
    #denom = (max_ - min_)
    band_calc = band / 40000
    band_new += band_calc
#band_new = (band_new * data_array[0] / data_array[3]) / 4
band_new = band_new / ndvi(data_array[3], data_array[2])
proc[0].close('__temp__')
proc[0].array_to_dataset('__temp__', band_new, copy=dataset, param={'band_num': 1, 'dtype': 6})
proc[0].save('__temp__', r'C:\sadkov\tulun\0107\test.tif')
'''
#proc.image_system = ['Sentinel']
proc.return_bands = True
proc.filter_clouds = True
proc.ath_corr_method = 'DOS1'
proc.input(r'C:\sadkov\tulun\sentinel')
proc.input(r'c:\sadkov\tulun\LC08_L1TP_138022_20190623_20190623_01_RT')
#print(proc.input_list)
dem = gdal.Open(r'C:\sadkov\tulun\alos\alos_crop_2019-06-29.tif')
for i in [1]:
    s = proc[i]
    '''
    #for key in s.file_names: print(key)
    s.ndwi('DOS1')
    if s.image_system == 'Landsat':
        s.mask('3')
        s.mask('4')
        mask_list = ['3', '5']
    elif s.image_system == 'Sentinel':
        s.mask('3')
        s.mask('8')
        mask_list = ['3', '8']
    else:
        print('Unreckognized image system, cannot create masks')
        mask_list = []
    if proc.filter_clouds:
        mask_list.append('Cloud')
        if s.image_system == 'Landsat':
            s.mask('QUALITY', 2720, True, 'Cloud')
        elif s.image_system == 'Sentinel':
            vector_path = s.meta_call('MASK_FILENAME', check={'type': 'MSK_CLOUDS'}, mtd=True)
            vector_path = '{}\\{}'.format(s.folder, vector_path)
            if os.path.exists(vector_path):
                s.vector_mask(vector_path, 'Cloud')
            else:
                print('Vector mask not found: {}'.format(vector_path))
        else:
            print('Unreckognized image system, cannot create cloud mask')
            mask_list.remove('Cloud')
    s.save('NDWI_DOS1', r'C:\sadkov\tulun\raster\ndwi_{}_{}.tif'.format(s.image_system, s.date), mask_list=mask_list)
    '''
    ndwi = gdal.Open(r'C:\sadkov\tulun\raster\ndwi_{}_{}.tif'.format(s.image_system, s.date))
    water = band2raster(ndwi, dem, method=gdal.GRA_Min, dtype=ndwi.GetRasterBand(1).DataType).ReadAsArray()
    s.array_to_dataset('water_0', water, copy=dem, param={'dtype': 6})
    #s.save('water_0', r'C:\sadkov\tulun\raster\water0_{}_{}.tif'.format(s.image_system, s.date))
    water[water > 0] = 0
    water[water < 0] = 1
    print(np.unique(water, return_counts=True))
    water_new = fill_by_mask(dem.ReadAsArray(), water, iter_num=100)
    s.array_to_dataset('Water', water, copy=dem, param={'dtype': 1})
    s.save('Water', r'C:\sadkov\tulun\raster\Water_{}_{}.tif'.format(s.image_system, s.date))
    s.mask('Water')
    s.save_to_shp('Water', r'C:\sadkov\tulun\raster\water_by_ndwi&dem_{}.shp'.format(s.date), mask_list=['Water'])
    #s.save_to_shp('NDBI_DOS1', r'C:\sadkov\tulun\export\water_by_ndwi_{}.shp'.format(s.date), mask_list=['3', '5', 'NDWI_DOS1'], classify_param={'borders': [0]})
    del s
    proc.close_scenes()

# Returns an array of 1 - water and 0 - no water
def ndwi2water(ndwi_array,          # source ndwi array
               threshold = 0,       # threshold value of water
               erosion = 0,         # number of erosion operations to the water array by 4-neighbour rule
               dem_array = None):   # DEM array which pit would be filled if they are lower than neigbouring water. Must be of the same shape as the ndwi_array!
    water_array = ndwi_array - threshold
    water_array[water_array > 0] = 0
    water_array[water_array < 0] = 1
    if erosion:
        water_array = erode(water_array, iter_num = erosion)
    if dem is not None:
        if dem.shape == water_array.shape:
            water_array = fill_by_mask(dem_array, water_array, iter_num=100)
        else:
            print("Array shapes do not match, cannot fill by dem")
    return water_array

'''
#proc.input(r'C:\sadkov\sentinel\new\S2A_MSIL1C_20180622T080611_N0206_R078_T37TGN_20180622T092729.SAFE')
proc.output_path = r'C:\sadkov\tulun\export'
#ss = proc[1]
#proc.input('C:\\sadkov\\lsat8')
#proc.input('C:\\sadkov\\sentinel')
#proc[0].ndwi('None')
#proc.run('ndwi')

#proc.composite(22, interpol_method=gdal.GRA_Average)


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
