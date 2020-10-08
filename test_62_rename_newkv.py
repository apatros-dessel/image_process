from geodata import *
from image_processor import process

pin = r'd:\digital_earth\KV_Nizhniy'
sour = r'\\172.21.195.2\FTP-Share\ftp\20200713_kanopus'
name_tmpt = r'KV.*_S_'

_file_types = {
        'DATA': '.tif',
        'RGB':  '.RGB.tif',
        'QL':   '.QL.tif',
        'IMG':  '.IMG.tif',
        'META': '.json',
    }

class s3folder():

    silent = False

    def __init__(self, path):
        self.files = None
        if os.path.isdir(path):
            if os.path.exists(path):
                corner, id = os.path.split(path)
                self.corner = corner
                self.id = id
                self.full = path
                files = []
                self.types = globals()['_file_types']
                for key in self.types:
                    ending = self.types[key]
                    file = fullpath(path,id+ending)
                    if os.path.exists(file):
                        files.append(key)
                if 'DATA' in files:
                    self.files = files

    def __bool__(self):
        return bool(self.files)

    def __str__(self):
        return '{}: {}'.format(self.id, ', '.join(self.files))

    def FinError(self, message):
        if not globals()['silent']:
            print(message)
        del self

    def RasterMatch(self, raster_path):
        return raster_match(fullpath(self.full,self.id,'tif'), raster_path)

    def RepairByScene(self, scene_path):
        proc = process().input(scene_path)
        scene = proc.scenes[0]
        newid = scene.meta.id.replace('.MS.','.PMS.')
        for key in self.files:
            try:
                os.rename(fullpath(self.full, self.id+self.types[key]), fullpath(self.full, newid+self.types[key]))
            except:
                pass
        if not 'META' in self.files:
            proc.GetCoverJSON(fullpath(self.full, newid+self.types['META']))
            self.files.append('META')
        get_pms_json(fullpath(self.full, newid+self.types['META']), fullpath(self.full, newid+self.types['DATA']))
        new_full = fullpath(self.corner, newid)
        try:
            os.rename(self.full, new_full)
        except:
            pass
        self.full = new_full
        self.id = newid

def backid(n):
    id = n.replace('.QL','').replace('.RGB','').replace('PSS4','PSS1')
    return id

def raster_params(pin):
    ds = gdal.Open(pin)
    if ds is None:
        print('Raster not found: %s' % pin)
        return None
    srs = get_srs(ds)
    geom = raster_geom(ds, srs)
    return srs, geom

def raster_match(path1, path2):
    geosrs1 = raster_params(path1)
    geosrs2 = raster_params(path2)
    if None in (geosrs1, geosrs2):
        return None, None
    else:
        srs1, geom1 = geosrs1
        srs2, geom2 = geosrs2
    crs_match = srs1.GetAttrValue('AUTHORITY',1) == srs2.GetAttrValue('AUTHORITY',1)
    # print(srs1.GetAttrValue('AUTHORITY',1), srs2.GetAttrValue('AUTHORITY',1), crs_match)
    if not crs_match:
        geom1.TransformTo(srs2)
    result = 2 * int(geom1.Intersects(geom2)) + crs_match
    return result

def raster_geom(ds, reference=None):
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
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

def get_pms_json(path_out, pms_raster_path):
    '''
    if os.path.exists(path_out):
        filter_dataset_by_col(path_dict['json'], 'id', pms_id, path_out=path_out)
        old_ds, old_lyr = get_lyr_by_path(path_out)
        if len(old_lyr) > 0:
            return 0

    # print('Original PMS data not found for %s, collecting data from MS' % pms_id)

    if not os.path.exists(path_cover):
        print('Cannot find path: {}'.format(path_cover))
        return 1

    ms_id = pms_id.replace('.PMS', '.MS')
    filter_dataset_by_col(path_cover, 'id', ms_id, path_out=path_out)
    '''
    pms_ds, pms_lyr = get_lyr_by_path(path_out, 1)

    feat = pms_lyr.GetNextFeature()
    feat.SetField('id', feat.GetField('id').replace('.MS.','.PMS.'))
    feat.SetField('id_neuro', feat.GetField('id_neuro') + 'PMS')
    feat.SetField('type', 'PMS')

    if os.path.exists(pms_raster_path):
        pms_data = gdal.Open(pms_raster_path)
    else:
        pms_data = None
    if pms_data is not None:
        feat.SetField('rows', int(pms_data.RasterYSize))
        feat.SetField('cols', int(pms_data.RasterXSize))
        feat.SetField('x_size', float(pms_data.GetGeoTransform()[0]))
        feat.SetField('y_size', -float(pms_data.GetGeoTransform()[5]))
    else:
        print('Raster not found: %s' % pms_raster_path)
        '''
        pan_id = pms_id.replace('.PMS', '.PAN')
        tpan_path = filter_dataset_by_col(path_cover, 'id', pan_id)
        pan_ds, pan_lyr = get_lyr_by_path(tpan_path)
        pan_feat = pan_lyr.GetNextFeature()
        feat.SetField('rows', int(pan_feat.GetField('rows')))
        feat.SetField('cols', int(pan_feat.GetField('cols')))
        feat.SetField('x_size', float(pan_feat.GetField('x_size')))
        feat.SetField('y_size', float(pan_feat.GetField('y_size')))
        '''
    # feat.SetField('area', None)

    pms_lyr.SetFeature(feat)

    pms_ds = None

    if pms_data:
        print('PMS data successfully written for for: %s' % path_out)

    return 0

sour_files = {}
for file in folder_paths(sour,1,'tif'):
    f,n,e = split3(file)
    if re.search(name_tmpt,n):
        if n in sour_files:
            sour_files[n].append(file)
        else:
            sour_files[n] = [file]

s3data = {}
for folder in folder_paths(pin)[0]:
    s3scene = s3folder(folder)
    if s3scene:
        s3data[s3scene.id.replace('PSS4','S')] = s3scene
        # print(s3scene.id.replace('PSS4','S'), s3scene.files)

# scroll(s3data)

for id in s3data:
    if id in sour_files:
        # print(sour_files[id])
        for rpath in sour_files[id]:
            if s3data[id].RasterMatch(rpath)==3:
                s3data[id].RepairByScene(os.path.dirname(rpath))