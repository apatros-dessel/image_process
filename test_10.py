# -*- coding: utf-8 -*-

# Makes composition of several channels in a scene

from image_process import *

proc = process()
#proc.input(r'C:\sadkov\tukolon\images\2016\S2A_MSIL1C_20160730T040552_N0204_R047_T48UXG_20160730T041151.SAFE')
#proc.input(r'c:\sadkov\tukolon\снимки\2016\LC08_L1TP_133021_20160627_20170323_01_T1')
proc.input(r'c:\sadkov\tukolon')
#proc.input(r'C:\sadkov\tulun\sentinel')
proc.output_path = r'c:\sadkov'
proc.tdir = r'c:\sadkov\temp'
proc.ath_corr_method = 'DOS1'
proc.filter_clouds = True
proc.return_bands = True

#vector_ds = ogr.Open(r'C:\sadkov\tukolon\tukolon_border.shp')
#proc[1].crop_band('4', vector_ds, save_path=r'c:\sadkov', crop_vector=True)
#proc[1] = proc[1].crop_scene(vector_ds, path=r'c:\sadkov\temp')
#print(s[4])
#s.save('4', r'c:\sadkov\4.tif')
t = dtime.datetime.now()
proc.input_vector(r'C:\sadkov\tukolon\tukolon_border.shp')
#proc.composite['band_list'] = [2,3,4,8]
#proc.composite['name'] = None
proc.composite['orig'] = False
proc.ath_corr_method = 'DOS1'
for scene_id in range(len(proc)):
    if proc[scene_id].date == dtime.date(2016, 7, 7):
        #proc.vector_crop(scene_id)
        proc.composition(scene_id)
#s = proc[0]
#s = s.crop_scene(vector_ds)

#s.composition('RGB')

#print(s.data_list)
#s.save('comp_RGB', r'c:\sadkov\tukolon\снимки\2016\{}_RGB.tif'.format(s.descript))
#proc.run('ndvi', crop_vector=r'C:\sadkov\tulun\adm_tulun.shp')
print(dtime.datetime.now()-t)
