from geodata import *
import argparse

parser = argparse.ArgumentParser(description='Path to raster data')
parser.add_argument('-o', default=None, dest='repxls', help='Report filename')
parser.add_argument('dir_in', help='Path to corner dir')
args = parser.parse_args()
dir_in = args.dir_in
repxls = args.repxls
if repxls is None:
    repxls = fullpath(dir_in, 'report.xls')

files = folder_paths(dir_in,1,'tif')
final_report = OrderedDict()
for file in files:
    name = split3(file)[1]
    final_report[name] = RasterReport(file)
    print('Reported from: %s' % name)

dict_to_xls(repxls, final_report)