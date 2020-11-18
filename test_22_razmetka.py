from image_processor import *

path = [
    r'g:\planet',
    r'f:\rks\toropez',
    # r'f:\rks\tver\20190926',
    # r'f:\rks\toropez\planet\20190419',
]

vector_path = r'D:/digital_earth/data_2_razmetka/20200219/TVER_QUARRY_PLN_20200214.shp'
raster_path = r'D:/digital_earth/planet_rgb/fin/20190910/20190910_083349_0f3f_3B_AnalyticMS.tif'
path_to_mask = r'E:\test\mask2.tif'

# ds_in = geodata.ogr.Open(vector_path, 1)

path_out = geodata.filter_dataset_by_col(vector_path, 'image', '20190910_083349_0f3f_3B_AnalyticMS_SR')

path = r'd:\digital_earth\data_2_razmetka\20200220'
export_folder = r'd:\digital_earth\data_2_razmetka\20200220'

folders, files = fold_finder(path)
for folder in folders:
    vector_path = raster_path = mask_path =  None
    for path2obj in os.listdir(folder):
        if path2obj.endswith('.shp'):
            vector_path = fullpath(folder, path2obj)
        if path2obj.endswith('.tif'):
            raster_path = fullpath(folder, path2obj)
            # mask_name = 'MWT' + path2obj[3:]
            mask_path = fullpath(export_folder, r'MWT' + path2obj[3:])
    if None in (vector_path, raster_path, mask_path):
        print('Data not found in: {}'.format(folder))
    else:
        # field_val_dict = geodata.split_vector_shp(vector_path, 'gridcode')
        geodata.RasterizeVector(vector_path, raster_path, mask_path, value_colname='gridcode', compress='LZW')
        '''
        scroll(field_val_dict)
        if len(field_val_dict)==1:
            geodata.RasterizeVector(vector_path, raster_path, mask_path, burn_value=int(field_val_dict.keys()[0]), compress='LZW')
        else:
            ds_out = geodata.ds(mask_path, copypath=raster_path, options = {'dt': 1, 'bandnum': 1, 'nodata': 0}, editable=True)
            arr = ds_out.GetRasterBand(1).ReadAsArray()
            for field_val in field_val_dict:
                # ds_out = geodata.gdal.Open(mask_path, 1)
                temp_mask_path = globals()['temp_dir_list'].create('tif')
                geodata.RasterizeVector(field_val_dict[field_val], raster_path, temp_mask_path, burn_value=int(field_val), compress='LZW')
                new_arr = geodata.get_band_array((temp_mask_path, 1))
                arr[new_arr!=0] = int(field_val)
                new_arr = None
            ds_out.GetRasterBand(1).WriteArray(arr)
            ds_out = None
        # if not geodata.RasterizeVector(vector_path, raster_path, mask_path, field_name='gridcode', compress='LZW'):
            # print('Saved mask {} for {}'.format(vector_path, raster_path))
        '''

# proc = process()
# proc.input(path, imsys_list=['PLN'])

# idlist = []
# for ascene in proc.scenes:
    # idlist.append(ascene.meta.name('[id]_[location]'))

# idarr = np.array(idlist)

# vals, counts = np.unique(idarr, return_counts=True)

# for id, count in zip(vals, counts):
    # print(id, count)

# scroll(locals())

# fin()