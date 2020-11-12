from geodata import *
import argparse

parser = argparse.ArgumentParser(description='Path to raster data')
parser.add_argument('-p', default=None, dest='path', help='Report filename')
parser.add_argument('xls', help='Path to corner dir')
args = parser.parse_args()
xls = args.xls
path = args.path
if xls:
    rep = xls_to_dict(xls)
    for name in rep:
        line = rep[name]
        if line.get('empty')=='True':
            id = name.replace('.IMG','').replace('.QL','').replace('.RGB','')
            file = r'%s\%s\%s.tif' % (path, id, name) # For S3-raster format only
            if path:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        print('DELETED: %s' % name)
                    except:
                        print('ERROR: %s' % name)
                else:
                    print('FILE NOT FOUND: %s' % file)
            else:
                print('TO DELETE: %s' % name)
        else:
            print('CORRECT: %s' % name)
else:
    print('XLS NOT FOUND: %s' % xls)
