# Creates water mask as shapefile from Landsat, Sentinel or Planet scene

# coding=utf-8

from image_processor import *

path2scenes = r'c:\sadkov\playground\test\planet'

proc = process(output_path=r'c:\\sadkov\playground\test')
proc.input(path2scenes)

for ascene in proc.scenes:
    #filename = ascene.name('test4planet_[date]_[imsys]_RGB.tif')
    #filepath = fullpath(proc.output_path, filename)
    #ascene.default_composite('RGB', filepath)
    #filename = ascene.name('test4planet_[date]_[imsys]_NIR.tif')
    #filepath = fullpath(proc.output_path, filename)
    #ascene.default_composite('NIR', filepath)
    #shpname = ascene.name('test4planet_mask_[date]_[imsys]_RGB.shp')
    #shppath = fullpath(proc.output_path, shpname)

    #raster_id, bandnum = ascene.band('red')
    #geodata.save_to_shp(ascene.getraster(raster_id), shppath, band_num=bandnum, classify_table = [[None, 1, 0], [1, None, 1]], export_values=[1])
    '''
    filelist = os.listdir(ascene.path)
    for file in filelist:
        if file.endswith('.json'):
            filepath = fullpath(ascene.path, file)
            shp = ogr.Open(filepath)
            if shp is not None:
                print('File opened: {}'.format(filepath))
    '''
    filename = ascene.name('test4planet_[date]_[imsys]_NDWI.tif')
    filepath = fullpath(proc.output_path, filename)
    ascene.calculate_index('NDWI', filepath)

#timecomposite(proc.scenes, ['red', 'red', 'green'], [0,1,0], r'c:\sadkov\playground\test\timecomp.tif')
