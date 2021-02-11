from geodata import *

pin = r'\\172.21.195.2\thematic\Sadkov_SA\sentinel-2'
pout = r'e:\rks\sentinel2s3'
suredir(pout)
path2delete = r'\\172.21.195.2\thematic\Sadkov_SA\sentinel-2\Sentinel-2_удалить.txt'
path2alter = r'\\172.21.195.2\thematic\Sadkov_SA\sentinel-2\Sentinel-2_поменять каналы.txt'

# Записать растр снимка в установленном формате
def repair_img(img_in, img_out, count, band_order=None, multiply = None):
    if band_order is None:
        band_order = range(1, count+1)
    raster = gdal.Open(img_in)
    new_raster = ds(img_out, copypath=img_in, options={'bandnum':count, 'dt':3, 'compress':'DEFLATE', 'nodata':0}, editable=True)
    for bin, bout in zip(band_order, range(1, count+1)):
        arr_ = raster.GetRasterBand(bin).ReadAsArray()
        o = np.unique(arr_)[0]
        arr_[arr_ == o] = 0
        if multiply is not None:
            if bin in multiply.keys():
                arr_ = arr_ * multiply[bin]
        new_raster.GetRasterBand(bout).WriteArray(arr_)
    raster = new_raster = None
    return img_out


with open(path2delete) as txt:
    del_list = txt.read().split('\n')
with open(path2alter) as txt:
    alter_list = txt.read().split('\n')

ids = []
objs = os.listdir(pin)
for obj in objs:
    folder = fullpath(pin, obj)
    if os.path.isdir(folder):
        out = None
        for id in alter_list:
            if id==obj:
                ids.append(obj)
                out_folder = fullpath(pout, obj)
                suredir(out_folder)
                names = os.listdir(folder)
                for name in names:
                    file = fullpath(folder, name)
                    file_out = fullpath(out_folder, name)
                    if name.endswith('json'):
                        shutil.copyfile(file, file_out)
                    elif name.endswith('tif'):
                        count = gdal.Open(file).RasterCount
                        if count==3:
                            shutil.copyfile(file, file_out)
                            print('COPY: %s' % name)
                        elif count in (4, 10):
                            if count==4:
                                band_order = [3,2,1,4]
                            elif count==10:
                                band_order = [3,2,1,8,4,5,6,7,9]
                            repair_img(fullpath(folder, name), fullpath(out_folder, name), count, band_order=band_order)
                        else:
                            print('WRONG COUNT: %s' % name)
                out = 'CHANGED'
                break
        for id in del_list:
            if id==obj:
                # print('TO DELETE: %s' % obj)
                out = 'DELETED'
                break
        if out is None:
            print('UNCLASSIFIED: %s' % obj)
        else:
            print('%s: %s' % (out, obj))

