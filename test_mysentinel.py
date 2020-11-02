from image_processor import *

path2sentinel = r'f:\rks\ghana\Sentinel-2\S2A_MSIL2A_20190507T102031_N0212_R065_T30NYP_20190520T110425.SAFE'
# path2kanopus = r'F:\rks\digital_earth\kanopus\tver_source\KV1_31813_25365_01_KANOPUS_20180416_085258_085407.SCN4.PMS.L2.DC.xml'

output_path = r'd:\digital_earth\neuro\n2'

proc = process(output_path=output_path)
proc.input(path2sentinel)
proc.get_vector_cover('vector_cover_full.json')

