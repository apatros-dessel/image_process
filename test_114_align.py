from script_razmetka_2 import *

ms = r'e:\temp\KV1_26056_20255_00_KANOPUS_20170402_091206_091239.SCN2.MS.L2.tif'
pan = r'e:\temp\KV1_26056_20255_00_KANOPUS_20170402_091206_091239.SCN2.PAN.L2.tif'
pan_repr = r'e:\temp\KV1_26056_20255_00_KANOPUS_20170402_091206_091239.SCN2.PAN.L2_REF.tif'

RasterAlign(pan, ms, pan_repr, tempdir = None, align_file = None, reproject_method = gdal.GRA_NearestNeighbour)