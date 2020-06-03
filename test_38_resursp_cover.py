from image_processor import *

path = r'\\tt-nas-archive\NAS-Archive-2TB-12\Kanopus\102_2020_126'
jsonpath = fullpath(path, '102_2020_126_Tver_fullcover.json')

proc = process().input(path)

proc.GetCoverJSON(jsonpath)