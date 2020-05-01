from geodata import *

# Make pansharpened image
def image_psh(ms, pan, psh, bands, bands_ref, enhanced):
    from pci.pansharp import *
    from pci.fexport import *
    fili = ms
    dbic = bands
    dbic_ref = bands_ref
    fili_pan = pan
    dbic_pan = [1]
    filo = psh.replace('.tif','.pix')
    dboc = dbic
    enhance = enhanced     # apply the color enhancement operation
    nodatval = [0.0]       # zero-valued pixels in any input image are excluded from processing
    poption = "OFF"        # resampling used to build pyramid overview images
    pansharp(fili, dbic, dbic_ref, fili_pan, dbic_pan, filo, dboc, enhance, nodatval, poption)
    fili = filo
    filo = psh
    dbiw = []
    dbic = dbic
    dbib = []
    dbvs = []
    dblut = []
    dbpct = []
    ftype =	"TIF"
    foptions = "TILED256"
    fexport( fili, filo, dbiw, dbic, dbib, dbvs, dblut, dbpct, ftype, foptions )
    if os.path.exists(filo):
        for file in (fili, filo+'.pox'):
            if os.path.exists(file):
                os.remove(file)

def raster_calculator(multi_raster_path, output_path, function):
    multi_raster_data = MultiRasterData(multi_raster_path, data=2)
    data_layers = []
    for arr in multi_raster_data:
        data_layers.append(arr)
    export = function(data_layers)
    del(data_layers)
    blue_ds = ds(output_path, copypath=ms_path, options={'bandnum': 1, 'compress': 'DEFLATE'}, editable=True)
    blue_ds.GetRasterBand(1).WriteArray(export)
    blue_ds = None

def new_blue(datas):
    red, green, nir = datas
    new_blue = (-0.14) * nir + 0.7 * green + 0.25 * red
    return new_blue.astype(np.uint16)

def correct_rsp(ms_path, pan_path, rgbn_path, pms_path):

    blue_calc_path = RasterMultiBandpath(ms_path, [1, 2, 4])

    blue_path = tempname('tif')

    raster_calculator(blue_calc_path, blue_path, new_blue)

    raster_band_paths = [
        (ms_path , 1), # RED
        (ms_path , 2), # GREEN
        (blue_path , 1), # BLUE
        (ms_path , 4),# NIR
        # ( r'F:/102_2020_108_RP/2020-02-02/2074508_22.01.20_Krym/RP1_36120_04_GEOTON_20191209_080522_080539.SCN1'
        # r'.MS_f13121466d65e41f5c181c84cb2e23d2c0553d9a/RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.MS.L2.tif' , 3),
        # old BLUE
    ]

    raster2raster(raster_band_paths, rgbn_path, method = gdal.GRA_NearestNeighbour, exclude_nodata = True, enforce_nodata = 0, compress = 'DEFLATE', overwrite = True)
    os.remove(blue_path)

    pms_temp = tempname('tif')
    image_psh(rgbn_path, pan_path, pms_path, [1,2,3,4], [1,2,3,4], 'YES')
    copydeflate(pms_temp, pms_path)
    os.remove(pms_temp)

    # raster2raster(raster_band_paths, output_path, method = gdal.GRA_NearestNeighbour, exclude_nodata = True, enforce_nodata = 0, compress = 'DEFLATE', overwrite = True)

ms_path = r''
pan_path = r'F:/102_2020_108_RP/2020-02-02/2074508_22.01.20_Krym/RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.PAN_bf9546c102d85f9bc9324a9b18eecb351675c3a0/RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.PAN.L2.tif'
rgbn_path = r'C:\Users\Home\Downloads\test_rgbn_5.tif'
pms_path = r'D:\terratech\resurs\RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.PMS.L2_old5.tif'

# correct_rsp(ms_path, pan_path, rgbn_path, pms_path)

# pms_temp = tempname('tif')
# image_psh(rgbn_path, pan_path, pms_temp, [1,2,3,4,5], [1,2,3,4,5], 'YES')
pms_temp = r'c:\Users\Home\AppData\Local\Temp\image_processor\2\0\0.tif'
copydeflate(pms_temp, pms_path, bigtiff = True, tiled = True)
# os.remove(pms_temp)