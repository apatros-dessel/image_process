from image_processor import *

path = r'e:\rks\source\kanopus\2020-06-19'
jsonpath = r'e:\rks\source\kanopus\2020-06-19\Krym_fullcover_new.json'

proc = process().input(path)

proc.GetCoverJSON(jsonpath)