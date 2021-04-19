from razmetka import *

pout = r'e:\rks\razmetka_source\kanopus_snow_new'

files = folder_paths(pout,1,'shp')

vals = {}

for file in files:
    f,id,e = split3(file)
    if not id in vals:
        if e.lower() in ('tif'):
            geom_path = RasterCentralPoint(gdal.Open(file), reference=None, vector_path=tempname('json'))
        elif e.lower() in ('shp', 'json'):
            geom_path = VectorCentralPoint(file, reference=None, vector_path=tempname('json'))
        if geom_path is not None:
            kan_id = GetKanopusId(id, type='MS', geom_path=geom_path)
            if kan_id != id:
                vals[id] = kan_id

for file in folder_paths(pout,1):
    f, id, e = split3(file)
    if id in vals:
        kan_id = vals[id]
        if kan_id is not None:
            rename(file, fullpath(f,kan_id,e))

scroll(vals)