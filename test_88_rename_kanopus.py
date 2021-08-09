from razmetka import *

pout = r'\\172.21.195.2\thematic\Sadkov_SA\razmetka_source\resurs_ms_mountain'
type = 'MS'
update = False
ending = ''

files = folder_paths(pout,1,['shp','tif','json'])

vals = {}
names = {}
name_duplicates = {}

for file in files:
    f,id,e = split3(file)
    name = '%s.%s' % (id, e)
    foldername = os.path.split(f)[1]
    tid = id
    end = ''
    if ending:
        if id.endswith(ending):
            tid, end = id.split(ending)
    if name in names:
        if name in name_duplicates:
            name_duplicates[name].append(foldername)
        else:
            name_duplicates[name] = [names[name], foldername]
    else:
        names[name] = foldername
    if not id in vals:
        if e.lower() in ('tif'):
            geom_path = RasterCentralPoint(gdal.Open(file), reference=None, vector_path=tempname('json'))
        elif e.lower() in ('shp', 'json'):
            geom_path = VectorCentralPoint(file, reference=None, vector_path=tempname('json'))
        # print(geom_path)
        if geom_path is not None:
            raster_dir = [None, f][update]
            kan_id = GetKanopusId(tid, type=type, geom_path=geom_path, raster_dir=raster_dir)
            if kan_id is not None:
                kan_id += ending
            if kan_id != id:
                vals[id] = kan_id

for file in folder_paths(pout,1):
    f, id, e = split3(file)
    if id in vals:
        kan_id = vals[id]
        if kan_id is not None:
            rename(file, fullpath(f,kan_id,e))

scroll(vals)

if len(name_duplicates)>0:
    scroll(name_duplicates, counts=True)