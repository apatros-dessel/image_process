from geodata import raster_data
import gdal
from datetime import datetime

input_path = r'c:\sadkov\rzd\severobaikalsk\forclip\Severobaikalsk_20191111_Pleiades.tif'
output_path = r'c:\sadkov\rzd\severobaikalsk\forclip\test.tif'

s_ds = gdal.Open(input_path)
t_ds = gdal.Open(output_path, 1)

t = datetime.now()
gdal.ReprojectImage(s_ds, t_ds)
print('Total time = {}'.format(datetime.now() - t))

# x = raster_data(input_path)
# for i in x:
    # print(i)