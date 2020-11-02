from geodata import *
import shutil
from pci.pansharp import *
from pci.fexport import *

# Make pansharpened image
def image_psh(ms, pan, psh, bands, bands_ref, enhanced, deflate=True):
    if deflate:
        finpath = psh
        psh = tempname('tif')
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
    if deflate:
        copydeflate(filo, finpath)
        os.remove(filo)
    if os.path.exists(filo):
        for file in (fili, filo+'.pox'):
            if os.path.exists(file):
                os.remove(file)

path_ms = r'd:\terratech\clouds_ms'
path_pan = r'f:\102_2020_126'
path_pms = r'd:\terratech\clouds_pms'

list_ms = os.listdir(path_ms)
list_pan = folder_paths(path_pan, files=True, extension='tif')
suredir(path_pms)

ok_list = []
error_list = []
lack_list = []

for i, file_ms in enumerate(list_ms):

    file_pan = file_ms.replace('.MS.', '.PAN.')
    file_pms = file_ms.replace('.MS.', '.PMS.')
    fin = False
    for filepath_pan in list_pan:
        if filepath_pan.endswith(file_pan):
            try:
                image_psh(fullpath(path_ms, file_ms),
                          filepath_pan,
                          fullpath(path_pms, file_pms),
                          [1,2,3,4], [1,2,3,4], 'YES')
                ok_list.append(file_pms)
                print('%i PMS written: %s' % (i+1, file_pms))
            except:
                print('%i Pansharpening error: %s' % (i+1, file_pms))
                error_list.append(file_pms)
            fin = True
            break

    if not fin:
        print('%i PAN not found: %s' % (i+1, file_pan))
        lack_list.append(file_pan)
        continue

scroll(ok_list, header='OK:')
print(len(ok_list))

scroll(error_list, header='ERRORS:')
print(len(error_list))

scroll(lack_list, header='MISSING:')
print(len(lack_list))
