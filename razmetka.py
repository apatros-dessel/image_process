from geodata import *

# Записать растр снимка в установленном формате
def RepairImage(img_in, img_out, count, band_order=None, multiply = None):
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
