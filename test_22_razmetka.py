from image_processor import *

path = [
    r'g:\planet',
    r'f:\rks\toropez',
    # r'f:\rks\tver\20190926',
    # r'f:\rks\toropez\planet\20190419',
]

vector_path = r'D:/digital_earth/data_2_razmetka/20200219/TVER_QUARRY_PLN_20200214.shp'
raster_path = r'D:/digital_earth/planet_rgb/fin/20190910/20190910_083349_0f3f_3B_AnalyticMS.tif'
path_to_mask = r'E:\test\mask.tif'

# ds_in = geodata.ogr.Open(vector_path, 1)

path_out = geodata.filter_dataset_by_col(vector_path, 'image', '20190910_083349_0f3f_3B_AnalyticMS_SR')

ds_out, lyr_out = geodata.get_lyr_by_path(path_out)

for feat in lyr_out:
    print(feat.GetField(feat.GetFieldIndex('id')), feat.GetField(feat.GetFieldIndex('image')))

geodata.RasterizeVector(path_out, raster_path, path_to_mask, compress='LZW')

# proc = process()
# proc.input(path, imsys_list=['PLN'])

# idlist = []
# for ascene in proc.scenes:
    # idlist.append(ascene.meta.name('[id]_[location]'))
    # print(ascene.meta.name('[id]_[location]'))

# idarr = np.array(idlist)

# vals, counts = np.unique(idarr, return_counts=True)

# for id, count in zip(vals, counts):
    # print(id, count)