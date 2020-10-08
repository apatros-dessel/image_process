from geodata import *
import pickle

path_in = r'\\172.21.195.2\FTP-Share\ftp'
txt_in = r'\\172.21.195.2\FTP-Share\ftp\file_list.txt'
pickle_scenes = r'\\172.21.195.2\FTP-Share\ftp\scenes.sdt'
aoi = r'D:/digital_earth/kemerovo/aoi_kemerovo.shp'
reference_dir = r'h:\References'
out_dir = r'd:\digital_earth\kemerovo\kemerovo_pms'
# _silent = True

tmpt_id_list = '^[fr0-9_]*KV\d_.*[LNBF0-9]$'

tmpt_pan = '^[fr0-9_]*KV\d_.*_PSS1_.*_\d{5}'
tmpt_ms = '^[fr0-9_]*KV\d_.*_S_.*_\d{5}'
tmpt_pms = '^[fr0-9_]*KV\d_.*_PSS4_.*_\d{5}'

tmpt_rgb = '^[fr0-9_]*KV\d_.*.RGB'
tmpt_ql = '^[fr0-9_]*KV\d_.*.QL'
tmpt_ref = '^[fr0-9_]*KV\d_.*.REF'

rsp_source_tmpt = r'.*RP.+PMS.L2[^\.]*$'
rsp_grn_tmpt = r'RP.+PMS.L2\..{0,3}\d{8}$'
rsp_rgb_tmpt = r'.*RP.+PMS.L2\..*\d*\.?RGB$'
rsp_ql_tmpt = r'.*RP.+PMS.L2\..*\.?QL$'
rsp_id_tmpt = r'RP.+PMS.L2'

tmpt_id_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_P?S+\d?_\d+_\d+',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.P?M?S?A?N?.L2',
]

tmpt_pan_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_PSS1_\d+_\d+',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PAN.L2',
]

tmpt_ms_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_S_\d+_\d+',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.MS.L2',
]

tmpt_pms_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_PSS4_\d+_\d+',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PMS.L2',
]

tmpt_rgb_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_PSS1_\d+_\d+.*\.RGB',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PAN.L2.*\.RGB',
]

tmpt_ql_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_PSS1_\d+_\d+.*\.QL',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PAN.L2.*\.QL',
]

tmpt_ref_list = [
    'fr\d+_KV[I0-9]_\d+_\d+_\d+_3NP2_\d+_PSS1_\d+_\d+.*\.REF',
    'KV[I0-9]_\d+_\d+_\d+_KANOPUS_\d+_\d+_\d+.SCN\d+.PAN.L2.*\.REF',
]

reference_in = folder_paths(reference_dir,1,'tif')

def sprint(s):
    _silent = globals().get('_silent')
    if _silent:
        print(s)

def RasterId(n):
    tmpt_id_list = globals()['tmpt_id_list']
    for tmpt_id in tmpt_id_list:
        search = re.search(tmpt_id, n)
        if search:
            id = search.group()
            id = id.replace('_PSS1','_S').replace('_PSS4','_S').replace('.PAN','.MS').replace('.PMS','.MS')
            return id

def RasterGeometry(ds_, reference=None):
    width = ds_.RasterXSize
    height = ds_.RasterYSize
    gt = ds_.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
    r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
    wkt = template % r1
    if sys.version.startswith('2'):
        geom = ogr.Geometry(wkt=wkt)
    else:
        geom = ogr.CreateGeometryFromWkt(wkt, reference)
    return geom

def CheckRasterParams(file):
    raster = gdal.Open(file)
    if raster:
        size = os.path.getsize(file)
        shape = (raster.RasterCount, raster.RasterXSize, raster.RasterYSize)
        geotransform = raster.GetGeoTransform()
        dtype = raster.GetRasterBand(1).DataType
        return (size, shape, geotransform, dtype)
    else:
        print('Cannot read file: %s' % file)
        return None

def ChooseRaster(files):
    file_fin = None
    size_fin = None
    shape_fin = None
    geotransform_fin = None
    dtype_fin = None
    for file in files:
        update = False
        if file:
            params = CheckRasterParams(file)
            if params:
                size, shape, geotransform, dtype = params
                if None in (file_fin, size_fin, shape_fin, geotransform_fin, dtype_fin):
                    update = True
                elif (shape_fin, geotransform_fin, dtype_fin)==(shape, geotransform, dtype):
                    if size<size_fin:
                        update = True
                else:
                    if size>size_fin:
                        update = True
                if update:
                    file_fin = file
                    size_fin = size
                    shape_fin = shape
                    geotransform_fin = geotransform
                    dtype_fin = dtype
        return file_fin

def Align(pin, ref, pout, tempdir=None, align_file=None, reproject_method=gdal.GRA_Bilinear):
    base = pin
    if tempdir is None:
        tempdir = os.environ['TMP']
    for tname in ('1.tif', '2.tif', '3.pickle'):
        tpath = fullpath(tempdir, tname)
        if os.path.exists(tpath):
            os.remove(tpath)
    transform = fullpath(tempdir, '3.pickle')
    srs_in = get_srs(gdal.Open(pin))
    srs_ref = get_srs(gdal.Open(ref))
    match = ds_match(srs_in, srs_ref)
    if not match:
        repr_raster = tempname('tif')
        ReprojectRaster(pin, repr_raster, int(srs_ref.GetAttrValue('AUTHORITY',1)), method=reproject_method)
        pin = repr_raster
    if align_file is None:
        align_file = pin
    elif align_file!=pin:
        srs_align = get_srs(gdal.Open(align_file))
        align_match = ds_match(srs_align, srs_ref)
        if not align_match:
            repr_raster = tempname('tif')
            ReprojectRaster(align_file, repr_raster, int(srs_ref.GetAttrValue('AUTHORITY', 1)), method=reproject_method)
            align_file = repr_raster
    cmd_autoalign = r'python37 C:\soft\rss_align-master\autoalign.py {align_file} {ref} {transform} -l -t {tempdir}'.format(
        align_file = align_file.replace(' ', '***'),
        ref = ref.replace(' ', '***'),
        transform = transform,
        tempdir = tempdir
    )
    print('\n%s\n' % cmd_autoalign)
    os.system(cmd_autoalign)
    if os.path.exists(transform):
        cmd_warp = r'python37 C:\soft\rss_align-master\warp.py {pin} {transform} {pout} -t {tempdir}'.format(
            pin = pin.replace(' ', '***'),
            transform = transform,
            pout = pout.replace(' ', '***'),
            tempdir = tempdir
        )
        os.system('\n%s\n' % cmd_warp)
        print('\nWRITTEN : %s' % pout)
    else:
        globals()['errors_list'].append(base)
        print('\nTRANSFORM NOT CREATED FOR: %s' % base)
    if not match:
        if os.path.exists(repr_raster):
            os.remove(repr_raster)

class SceneData():

    def __init__(self, id):
        self.id = id
        self.limits = None
        self.proj = None
        self.data = {}
        self.blueprint = True

    def _Pack(self):
        export = {}
        export['id'] = self.id
        export['limits'] = self.limits
        export['proj'] = self.proj
        export['data'] = self.data
        export['blueprint'] = self.blueprint
        return export

    def AddLimits(self, raster_path):
        ds_ = gdal.Open(raster_path)
        if ds_:
            proj_ = ds_.GetProjection()
            if proj_:
                width = ds_.RasterXSize
                height = ds_.RasterYSize
                gt = ds_.GetGeoTransform()
                minx = gt[0]
                miny = gt[3] + width * gt[4] + height * gt[5]
                maxx = gt[0] + width * gt[1] + height * gt[2]
                maxy = gt[3]
                self.limits = (minx, miny, maxx, maxy)
                self.proj = proj_
                return None
        sprint('Error making limits from: %s' % raster_path)
        return None

    def SpatialReference(self):
        if self.proj is None:
            sprint('No projection data found, unable to get spatial reference: %s' % self.id)
            return None
        else:
            srs = osr.SpatialReference()
            srs.ImportFromWkt(self.proj)
            return srs

    def Limits(self):
        if None in (self.limits, self.proj):
            sprint('No scene limits found, unable to get limits: %s' % self.id)
            return None, None
        minx, miny, maxx, maxy = self.limits
        template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
        r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
        wkt = template % r1
        srs = self.SpatialReference()
        return ogr.CreateGeometryFromWkt(wkt, srs), srs

    def RasterDataMatch(self, ds_):
        if None in (self.limits, self.proj):
            sprint('No scene limits found, unable to get raster match: %s' % self.id)
            return None
        geom, srs = self.Limits()
        raster_geom = RasterGeometry(ds_, srs)
        return geom.Intersects(raster_geom)

    def VectorMatch(self, vec_path):
        if None in (self.limits, self.proj):
            sprint('No scene limits found, unable to get vector match: %s' % self.id)
            return None
        ds_, lyr_ = get_lyr_by_path(vec_path)
        if lyr_:
            geom, srs = self.Limits()
            srs_vec = lyr_.GetSpatialRef()
            if srs!=srs_vec:
                trans = osr.CoordinateTransformation(srs, srs_vec)
                geom.Transform(trans)
            for feat in lyr_:
                if geom.Intersects(feat.GetGeometryRef()):
                    return True
            return False
        else:
            print('Cannot get layer from %s, unable to get vector match' % vec_path)
            return None


    def Blueprint(self, status):
        for key in self.data:
            slice = self.data[key]
            if status:
                if not isinstance(slice, list):
                    self.data[key] = [slice]
            else:
                if isinstance(slice, list):
                    self.data[key] = ChooseRaster(slice)
        self.blueprint = status
        return self

    def AddRaster(self, file):
        tmpt_pan = globals()['tmpt_pan'] # '^[fr0-9_]*KV\d_.*_PSS1_.*_\d{5}'
        tmpt_ms = globals()['tmpt_ms'] # '^[fr0-9_]*KV\d_.*_S_.*_\d{5}'
        tmpt_pms = globals()['tmpt_pms'] # '^[fr0-9_]*KV\d_.*_PSS4_.*_\d{5}'
        tmpt_rgb = globals()['tmpt_rgb'] # '^[fr0-9_]*KV\d_.*.RGB'
        tmpt_ql = globals()['tmpt_ql'] # '^[fr0-9_]*KV\d_.*.QL'
        tmpt_ref = globals()['tmpt_ref']  # tmpt_ref = '^[fr0-9_]*KV\d_.*.REF'
        if os.path.exists(file):
            if not self.blueprint:
                print('Error: cannot update not a blueprint scene')
            else:
                f, n, e = split3(file)
                if re.search(tmpt_pan, n):
                    type = 'PAN'
                elif re.search(tmpt_ms, n):
                    type = 'MS'
                elif re.search(tmpt_pms, n):
                    type = 'PMS'
                else:
                    print('Wrong type: %s' % n)
                    type = None
                if type:
                    if re.search(tmpt_ql, n):
                        key = 'QL'
                    elif re.search(tmpt_rgb, n):
                        key = 'RGB'
                    else:
                        key = 'DATA'
                    if key!='DATA':
                        key_fin = '%s_%s' % (type, key)
                    else:
                        key_fin = type
                    if re.search(tmpt_ref, n):
                        key_fin += '_REF'
                    if key_fin in self.data:
                        if not file in self.data[key_fin]:
                            self.data[key_fin].append(file)
                    else:
                        self.data[key_fin] = [file]
                    if None in (self.limits, self.proj):
                        self.AddLimits(file)
        return self

    def Reproject(self, key, path_ref, reference_in=globals()['reference_in']):
        if self.blueprint:
            print('Cannot reproject not a blueprint scene: %s' % self.id)
        else:
            new_key = key + '_REF'
            if new_key in self.data:
                print('Key already exists: %s' % new_key)
            file = self.data.get(key)
            if file is None:
                print('File not found in scene: %s' % key)
            else:
                if key.startswith('MS') and (self.data.get('PAN')!=None):
                    align = self.data.get('PAN')
                else:
                    align = file
                fail = True
                intersect_dict = OrderedDict()
                for reference in reference_in:
                    match = raster_match(align, reference)
                    if match == 3:
                        align_system(file, reference, path_ref, align_file=align)
                        fail = False
                        break
                    else:
                        intersect_dict[ref] = match
                if fail:
                    # scroll(intersect_dict)
                    for ref in intersect_dict:
                        if intersect_dict[ref] == 2:
                            align_system(file, ref, pout, align_file=align, reproject_method=gdal.GRA_Bilinear)
                            fail = False
                            break
                if fail:
                    globals()['errors_list'].append(os.path.basename(file))
                    print('REFERENCE NOT FOUND FOR: %s' % file)
                else:
                    self.data[new_key] = path_ref

class SceneDataSet():

    def __init__(self):
        self.ids = {}
        self.set = []

    def __len__(self):
        return len(self.set)

    def __getattr__(self, item):
        return self.set[item]

    def Include(self, obj):
        if isinstance(obj, SceneData):
            id = obj.id
            geom, srs = obj.Limits()
        elif isinstance(obj, str):
            f,n,e = split3(obj)
            id = RasterId(n)
            ds_ = gdal.Open(obj)
            geom, srs = None, None
            if ds_:
                proj_ = ds_.GetProjection()
                if proj_:
                    srs = osr.SpatialReference()
                    srs.ImportFromWkt(proj_)
                    geom = RasterGeometry(ds_, srs)
        else:
            sprint('Wrong data for include: {}'.format(type(obj)))
            return None
        if None in (id, geom, srs):
            sprint('Data import error: {}'.format(type(obj)))
            return None
        elif id in self.ids:
            for item in self.ids[id]:
                old_scene_data = self.set[item]
                old_geom, old_srs = old_scene_data.Limits()
                if old_srs:
                    if srs!=old_srs:
                        trans = osr.CoordinateTransformation(old_srs, srs)
                        old_geom.Transform(trans)
                    if geom.Intersects(old_geom):
                        return item
                else:
                    sprint('Cannot get projection from old scene: %s' % old_scene_data.id)
                    return None
        else:
            return None

    def AddSceneData(self, scene_data):
        item = self.Include(scene_data)
        if item is None:
            id = scene_data.id
            item = len(self.set)
            self.ids[id] = [item]
            self.set.append(scene_data)
            return item
        else:
            sprint('Scene already exists: %s' % scene_data.id)
            return item

    def AddRaster(self, raster_path):
        item = self.Include(raster_path)
        if item is None:
            f,n,e = split3(raster_path)
            if n is None:
                print('Error raster path: {}'.format(raster_path))
            id = RasterId(n)
            if id:
                scene_data = SceneData(id)
                scene_data.AddRaster(raster_path)
                item = self.AddSceneData(scene_data)
            else:
                print('Cannot get id from: %s' % n)
                return None
        else:
            self.set[item].AddRaster(raster_path)
        return item

    def Blueprint(self, val):
        for scene_data in self.set:
            scene_data.Blueprint(val)
            print(scene_data.id)
        return self

class RasterMeta():

    def __init__(self, path_in):
        self.ok = False
        self.Update(path_in)
        return self

    def Update(self, path_in):
        if os.path.exists(path_in):
            f,n,e = split3(path_in)
            self.f = f
            self.n = n
            self.e = e
            raster = gdal.Open(path_in)
            if raster:
                self.bands = raster.RasterCount
                self.x = raster.RasterXSize
                self.y = raster.RasterYSize
                proj = raster.GetProjection()
                geotransform = raster.GetGeoTransform()
                if proj!=None and geotransform!=None:
                    self.prj = proj
                    self.gtr = geotransform
                    self.ok = True
        return self

    def Open(self):
        return gdal.Open(fullpath(self.f, self.n, self.e))

    def Geometry(self, srs = None):
        if self.Ok():
            return RasterGeometry(self.Open(), srs)

if txt_in:
    if os.path.exists(txt_in):
        files = open(txt_in).read().split('\n')
    else:
        files = None
if not files:
    files = folder_paths(path_in,1,'tif')
    if txt_in:
        with open(txt_in,'w') as txt:
            txt.write('\n'.join(files))
# names = flist(files, lambda x: split3(x)[1])
'''
result = OrderedDict()

result = pickle.loads(open(pickle_scenes, 'rb').read())

for i, id in enumerate(result):
    scene_data_list = result[id]
    # print(len(scene_data_list))
    for scene_data in scene_data_list:
        # print('\n%s' % scene_data.id)
        # scroll(scene_data.data, header='FIN')
        scene_data.Blueprint(True)
        # scroll(scene_data.data, header='BLUE')
        if scene_data.VectorMatch(aoi):
            # print(scene_data.id)
            ref = scene_data.data.get('PMS_REF')
            if ref:
                ref = ref[0]
                endpath = fullpath(out_dir, os.path.basename(ref))
                if os.path.exists(endpath):
                    print('PATH EXISTS: %s' % scene_data.id)
                else:
                    shutil.copyfile(ref, endpath)
                    print('FILE WRITTEN: %s' % scene_data.id)
            else:
                pms0 = scene_data.data.get('PMS')
                pan0 = scene_data.data.get('PAN_REF')
                ms0 = scene_data.data.get('MS_REF')
                if pms0:
                    endpath = fullpath(out_dir, os.path.basename(ref))
                    if os.path.exists(endpath):
                        print('PATH STILL EXISTS: %s' % scene_data.id)
                    else:
                        scene_data.Reproject('PMS', endpath)
                        print('NEW FILE CREATED: %s' % scene_data.id)
                elif pan0 and ms0:
                    print('PANSHARPENING IS NEEDED: %s' % scene_data.id)
                else:
                    print('NO REFERENCE FOUND: %s' % scene_data.id)
                    print(scene_data.data.keys())


new_files = folder_paths(r'e:\rks\ref',1,'tif')

count = 0
for file in files:
    #if count>=1:
        #break
    if not os.path.exists(file):
        continue
    f,n,e = split3(file)
    ds_ = gdal.Open(file)
    if ds_ is None:
        continue
    if re.search(tmpt_id,n):
        id = re.search(tmpt_id,n).group()
        id = id.replace('PSS4','S').replace('PSS1','S').replace('.REF','')
        miss = True
        if id in result:
            for scene_data in result[id]:
                if scene_data.RasterDataMatch(ds_):
                    scene_data.AddRaster(file)
                    miss = False
        else:
            result[id] = []
        if miss:
            result[id].append(SceneData(id))
            result[id][-1].AddRaster(file)
        count += 1
        print('New raster: %s' % file)

for id in result:
    scene_data_list = result[id]
    for scene_data in scene_data_list:
        # print('\n%s' % scene_data.id)
        # scroll(scene_data.data, header='BLUE')
        scene_data.Blueprint(False)
        scroll(scene_data.data, header='\n%s' % scene_data.id)

pack = scene_data._Pack()
# scroll(pack)
'''

result = SceneDataSet()

for file in files:
    item = result.AddRaster(file)
    if item is None:
        print('PASS: %s' % file)
    else:
        print('ADD:  %s' % file)

result.Blueprint(False)

try:
    with open(pickle_scenes,'wb') as bytes:
            bytes.write(pickle.dumps(result))
except:
    print('Error pickling')

pass