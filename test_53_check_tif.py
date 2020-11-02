from geodata import *

pin = r'\\TT-PC-10-Quadro\FTP_Share14TB\PLANET'
pout_txt = None

if pout_txt is None:
    pout_txt = fullpath(pin, 'error_dg.txt')

folders, files = folder_paths(pin, extension='tif', filter_folder=['GIS_FILES'])

report = []

for folder in folders:
    if len(folder_paths(folder,1,'tif'))==0:
        report.append('EMPTY FOLDER: %s' % folder)

for file in files:
    raster = gdal.Open(file)
    if raster is None:
        report.append('ERROR IN FILE: %s' % file)

with open(pout_txt, 'w') as txt:
    txt.write('\n'.join(report))