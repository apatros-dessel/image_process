# Unites a set of vector dataset into a single shape file preserving all the attributes

from shpwork import *
from image_processor import process, fullpath, scroll

path = r'C:\source\planet'
output_path = r'C:\sadkov\planet_tverskaya'

proc = process(output_path=output_path)
proc.input(path)

input_list = []
for ascene in proc.scenes:
    input_list.append(fullpath(proc.output_path, ascene.meta.datamask))
scroll(input_list)

gar = geoarray(geomtype='POLYGON')

for input_path in input_list:
    gar.import_from_shp(input_path, import_geometry=True)

gar.export_to_shp(output_path)