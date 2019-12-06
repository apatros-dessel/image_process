# Makes linear regression for two DEMs before subtraction

import os
import gdal
import numpy as np
from sklearn.linear_model import LinearRegression

path = r'C:\sadkov\forest\Sept_test\dem\kluchevskoie\tif'
dem1path = r'dem_topo_Kluchevskoie_shifted2alos.tif'
dem2path = r'DEM_alos_Kluchevskoie.tif'
dem1_adapted_path = r'dem_topo_Kluchevskoie_shifted2alos_adapted.tif'


os.chdir(path)
dem1 = gdal.Open(dem1path).ReadAsArray()
dem2 = gdal.Open(dem2path).ReadAsArray()


assert dem1.shape == dem2.shape

x = dem1.reshape((-1,1))
y = dem2.reshape((-1,1))


model = LinearRegression().fit(x,y)
print('Coefficient of determination = ', model.score(x, y))
print('Intercept = ', model.intercept_)
print('Slope = ', model.coef_[0])

dem1_adapted = dem1 * model.coef_[0] + model.intercept_

driver = gdal.GetDriverByName('GTiff')
outData = driver.CreateCopy(dem1_adapted_path, gdal.Open(dem1path), 1)
outData.GetRasterBand(1).WriteArray(dem1_adapted)
outData = None
'''
data = np.hstack((x, y))

fig, (ax1, ax2) = plt.subplots(nrows = 1, ncols = 2, figsize = (100,100))
ax1.scatter(x=dem1, y=dem2)
ax1.set_title('DEM 1-2')

ax2.hist(data, bins=np.arange(data.min(), data.max()), label=('DEM_topo', 'DEM_srtm'))

plt.show()
'''
