# -*- coding: utf-8 -*-

# Makes time composites of Landsat/Sentinel-2 data

from image_process import *

interpol_method_eng = ['Nearest Neighbour', 'Average', 'Bilinear', 'Cubic', 'Cubicspline', 'Lanczos']
interpol_method_rus = ['Ближайший сосед', 'Среднее', 'Билинейная', 'Кубическая', 'Кубический сплайн', 'Lanczos']
interpol_method = [gdal.GRA_NearestNeighbour, gdal.GRA_Average, gdal.GRA_Bilinear, gdal.GRA_Cubic, gdal.GRA_CubicSpline, gdal.GRA_Lanczos]

def create_virtual_dataset(proj, geotrans, shape_, num_bands):
    y_res, x_res = shape_
    ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, num_bands, gdal.GDT_Byte)
    ds.SetGeoTransform(geotrans)
    ds.SetProjection(proj)
    return ds

def reproject_band(band, s_proj, s_trans, t_proj, t_trans, t_shape, dtype, method=gdal.GRA_Bilinear):
    y_size, x_size = band.shape
    driver = gdal.GetDriverByName('MEM')
    s_ds = driver.Create('', x_size, y_size, 0)
    s_ds.AddBand(dtype)
    s_ds.GetRasterBand(1).WriteArray(band)
    s_ds.SetGeoTransform(s_trans)
    s_ds.SetProjection(s_proj)
    t_ds = driver.Create('', t_shape[1], t_shape[0], 0)
    t_ds.AddBand(dtype)
    t_ds.SetGeoTransform(t_trans)
    t_ds.SetProjection(t_proj)
    gdal.ReprojectImage(s_ds, t_ds, None, None, method)
    return t_ds.ReadAsArray()

def band2raster(s_raster_path, t_raster, s_band_num, method):
    os.chdir(os.path.split(s_raster_path)[0])
    s_raster = gdal.Open(os.path.split(s_raster_path)[1])
    s_proj = s_raster.GetProjection()
    s_trans = s_raster.GetGeoTransform()
    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    if s_band_num > s_raster.RasterCount:
        s_band_num = s_raster.RasterCount
    s_band_array = s_raster.GetRasterBand(s_band_num).ReadAsArray()
    dtype = s_raster.GetRasterBand(s_band_num).DataType
    t_band_array = reproject_band(s_band_array, s_proj, s_trans,t_proj, t_trans, t_shape, dtype, method)
    t_raster.AddBand(dtype)
    t_raster.GetRasterBand(t_raster.RasterCount).WriteArray(t_band_array)
    return t_raster.RasterCount

def raster2raster(path2start, path2target, path2export, band_list, method=gdal.GRA_Bilinear):
    len_ = len(path2start)
    while len(band_list) < len_:
        band_list.append(band_list[-1])
    os.chdir(os.path.split(path2target)[0])
    t_raster = gdal.Open(os.path.split(path2target)[1])
    t_proj = t_raster.GetProjection()
    t_trans = t_raster.GetGeoTransform()
    t_shape = (t_raster.RasterYSize, t_raster.RasterXSize)
    ds = create_virtual_dataset(t_proj, t_trans, t_shape, 0)
    for id in range(len_):
        band2raster(path2start[id], ds, band_list[id], method)
    driver = gdal.GetDriverByName('GTiff')
    os.chdir(os.path.split(path2export)[0])
    outputData = driver.CreateCopy(os.path.split(path2export)[1], ds, len(band_list))
    outputData = None
    return

def dual_composite(new_scene, old_scene, method='nRoRnG'):
    new_red = '{}/{}'.format(new_scene.folder, )
    path2start = [self.dlg.lineEdit.text().strip(), self.dlg.lineEdit_3.text().strip(),
                  self.dlg.lineEdit_5.text().strip()]
    path2target = self.dlg.lineEdit_7.text().strip()
    path2export = self.dlg.lineEdit_8.text().strip()
    band_list = [int(self.dlg.lineEdit_2.text().strip()), int(self.dlg.lineEdit_4.text().strip()),
                 int(self.dlg.lineEdit_6.text().strip())]
    method = interpol_method[self.dlg.comboBox.currentIndex()]

    raster2raster(path2start, path2target, path2export, band_list, method)

input_path = ''

proc = process()
proc.input(input_path)

for scene in proc:



proc.input(r'c:\sadkov\tukolon')
proc.output_path = r'c:\sadkov'
proc.tdir = r'c:\sadkov\temp'
proc.ath_corr_method = 'DOS1'
proc.filter_clouds = True
proc.return_bands = True

vector_ds = ogr.Open(r'C:\sadkov\tukolon\tukolon_border.shp')

# Pairing images by row and column
for scene in proc:
    if scene.date == dtime.date(2016, 7, 7):
        s = scene
#s = proc[0]
s = s.crop_scene(vector_ds)

s.composition('RGB')

print(s.data_list)
s.save('comp_RGB', r'c:\sadkov\tukolon\снимки\2016\{}_RGB.tif'.format(s.descript))
#proc.run('ndvi', crop_vector=r'C:\sadkov\tulun\adm_tulun.shp')
print(dtime.datetime.now()-t)
