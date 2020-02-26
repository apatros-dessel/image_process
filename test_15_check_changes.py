# -*- coding: utf-8 -*-

# Checks changes between two space images and saves it as vector or raster

from image_process import *

proc = process()
proc.input('c:\source\landsat\kirenskoie\LC08_L1TP_131019_20170531_20170615_01_T1')
proc.output_path = 'c:\Temp'
proc.work_method = 'Single'
proc.image_system = 'All'
proc.ath_corr_method = 'None'
proc.return_bands = False
proc.filter_clouds = False
vectorize = True
erosion = 0
threshold = 0.1

#proc.nbr_new(proc.output_path, vectorize=True, threshold=threshold, erosion=erosion)

band_dict = 0

import mylandsat
mtl = mylandsat.mtl2list('c:\source\landsat\kirenskoie\LC08_L1TP_133020_20160830_20170321_01_T1\LC08_L1TP_133020_20160830_20170321_01_T1_MTL.txt')

x = iter(mylandsat.mtl_iter(mtl))
print(next(x))

