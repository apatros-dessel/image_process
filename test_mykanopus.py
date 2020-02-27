# -*- coding: utf-8 -*-

from image_processor import *

path2kanopus = r'd:\digital_earth\kanopus_new\krym'
# path2kanopus = r'F:\rks\digital_earth\kanopus\tver_source\KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2.DC.xml'

output_path = r'e:\test'

proc = process(output_path = r'e:\test').input(path2kanopus)
proc.get_vector_cover(r'kanopus_vector_cover_full.json')

