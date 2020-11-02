from image_processor import *

pin = r'\\172.21.195.2\FTP-Share\ftp\images\102_2020_1159\2020-07-05\2179551_04.07.20_Крым\KV3_13273_10498_00_KANOPUS_20200624_084355_084426.SCN1.MS_63f7cbd3c2c5aca64338e00fb19a2c9087356e3a'
pout = None
prenom = '102_2020_1159.'

def SetMetaFromRaster(raster_path, output_path = None, prenom = ''):
    f, n, e = split3(raster_path)
    if output_path is None:
        output_path = f
    proc = process().input(f)
    if len(proc) == 1:
        name = prenom + n
        proc.GetCoverJSON(fullpath(output_path, name, 'json'))
        print('Done: %s' % name)
    else:
        print('Error: %s' % n)

for path in folder_paths(pin,1,'tif'):
    SetMetaFromRaster(path, output_path = pout, prenom = prenom)