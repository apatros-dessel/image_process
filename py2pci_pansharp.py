# -*- coding: utf-8 -*-

from geodata import *
import argparse

try:
    from pci.pansharp import *
    from pci.fexport import *
except:
    print('\nPCI GEOMATICA not available.\n')
    sys.exit(1)

def StringToListInteger(str_):
    if str_ is None:
        return None
    if isinstance(str_, list):
        return flist(str_, int)
    list0 = str_.split(' ')
    list_fin = []
    for val0 in list0:
        list1 = val0.split(',')
        for val1 in list1:
            if val1:
                digit = re.search(r'\d+', val1)
                if digit:
                    list_fin.append(int(digit.group()))
    return list_fin

# Make pansharpened image
def image_psh(ms, pan, psh, bands, bands_ref, enhanced):
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

parser = argparse.ArgumentParser(description='Given 2 geotiff images finds transformation between')
parser.add_argument('-b', default=None, dest='bands', help='Bands order')
# parser.add_argument('-br', default=[1,2,3,4], dest='bands_ref', help='Bands ref order')
parser.add_argument('-e', default='YES', dest='enhanced', help='Enhanced ("YES"/"NO")')
parser.add_argument('-d', default=False, dest='deflate', help='File compression')
parser.add_argument('pan_in', help='Input PAN tif')
parser.add_argument('ms_in', help='Input MS tif')
parser.add_argument('pms_out', help='Output PMS tif')
args = parser.parse_args()
pan_in = args.pan_in.replace('!!!!!!!','&')
ms_in = args.ms_in.replace('!!!!!!!','&')
pms_out = args.pms_out.replace('!!!!!!!','&')
bands = StringToListInteger(args.bands)
# bands_ref = StringToListInteger(args.bands_ref)
enhanced = args.enhanced.upper()
deflate = bool(args.deflate)

if bands is None:
    raster = gdal.Open(ms_in)
    if raster is None:
        print('CANNOT OPEN FILE: %s' % ms_in)
        sys.exit()
    bands = list(range(1, raster.RasterCount + 1))
    del raster
bands_ref = bands

if deflate:
    t_pms = tempname('tif')
    image_psh(ms_in, pan_in, t_pms, bands, bands_ref, enhanced)
    copydeflate(t_pms, pms_out, bigtiff=True, tiled=True)
    os.remove(t_pms)
else:
    image_psh(ms_in, pan_in, pms_out, bands, bands_ref, enhanced)