from image_processor import *

path = r'\\tt-nas-archive\Dockstation-HDD\102_2020_108_PSH'
jsonpath = fullpath(path, 'Resurs_krym_new_fullcover.json')

proc = process().input(path)

proc.GetCoverJSON(jsonpath)