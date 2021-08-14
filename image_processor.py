# -*- coding: utf-8 -*-

# Version 0.3

from tools import *

import geodata

# import mylandsat
import myplanet, mykanopus, mysentinel, myresursp, mydg, myskysat, myrapideye, mypleiades, mymeteor, mykshmsa
import mylandsat2 as mylandsat

# Constants

default_output = os.getcwd() # default output directory for a process

metalib = {
    'LST': mylandsat,
    'SNT': mysentinel,
    'PLN': myplanet,
    'KAN': mykanopus,
    'RSP': myresursp,
    'DG': mydg,
    'SS': myskysat,
    'RYE': myrapideye,
    'PLD': mypleiades,
    'MET': mymeteor,
    'KSH': mykshmsa,
}

# A dictionary of metadata filenames templates
template_dict = {}
for key in metalib:
    template_dict[key] = metalib[key].templates

# Set default types of composites
composites_dict = {
    'RGB':      ['red', 'green', 'blue'],           # Natural colours
    'NIR':      ['nir', 'red', 'green'],            # False colours
    'UFC':      ['swir2', 'swir1', 'red'],          # Urban False Colour
    'AGR':      ['swir1', 'nir', 'blue'],           # Agriculture
    'GEOL':     ['swir2', 'red', 'blue'],           # Geology
    'BAT':      ['red', 'green', 'coastal'],        # Bathymetric
    'APN':      ['swir2', 'swir1', 'narrow nir'],   # Athmospheric penetration
    'SWIR':     ['swir2', 'narow nir', 'red'],
    'SWIR-2':   ['blue', 'swir1', 'swir2'],
    'RGBN':     ['red', 'green', 'blue', 'nir'],    # Four channels for image classification
    'FAR':      ['swir1', 'nir', 'green'],          # Previously unmentioned synthesis from A.Cherepanov fire detection algorithm
}

# Set default types of indices
index_dict = {
    'NDVI':     ('Normalized',              ['nir', 'red'],     6,  'Reflectance'),
    'NDWI':     ('Normalized',              ['nir', 'green'],   6,  'Reflectance'),
    'NDBI':     ('Normalized',              ['swir', 'nir'],    6,  'Reflectance'),
    'NDVIadj':  ('NormalizedAdjusted',      ['nir', 'red'],    6,  'Reflectance'),
}

# Set elements for naming files
nameids = {
    '[imsys]':  3,
    '[sat]':    3,
    '[place]':  6,
    '[date]':   8,
    '[year]':   4,
    '[month]':  2,
    '[day]':    2,
}

# Product types list
product_types_list = [
    'Radiance',
    'Reflectance'
]

# Product types for work and GDAL datatypes for them
raster_product_types = {
    'Radiance':     7,
    'Reflectance':  7,
}

# Returns product generation function
def get_product_generation_function(imsys, prodid):

    func = globals()['metalib'].get(imsys).product_func.get(prodid)

    if hasattr(func, '__repr__'):
        return func

    else:
        print('"{}" product function not found for "{}"'.format(prodid, imsys))
        return None

temp_dir_list_ip = tdir(default_temp) # tdir object for working with temporary files

# Class containing image processing parameters and procedures
class process(object):

    def __init__(self,
                 output_path=globals()['default_output'],
                 #image_system = globals()['image_system_list'],
                 #work_method = globals()['work_method_list'][0],
                 tdir = globals()['default_temp']):

        self.output_path = output_path  # must be dir
        self.ids = []
        self.scenes = []  # contains available scenes
        self.options = {}
        self.tdir = tdir

    def __str__(self):
        return 'Process of {} scenes available'.format(len(self.scenes))

    # Returns number of paths in the input_list
    def __len__(self):
        return len(self.scenes)

    # Checks if a single path is available in the input_list
    def __bool__(self):
        return bool(self.scenes)

    # Adds new path to self.input_list
    def add_scene(self, newpath, imsys, skip_duplicates = True):
        newscene = scene(newpath, imsys)
        try:
            newscene = scene(newpath, imsys)
        except:
            print('Cannot open {} scene by path: {}'.format(imsys, newpath))
            newscene = None
        if newscene is not None:
            if newscene.meta.id in self.ids:
                if skip_duplicates:
                    print('ID duplicate: {}'.format(newscene.meta.id))
                    return self
            self.scenes.append(newscene)
            self.ids.append(newscene.meta.id)
        return self

    def input(self, path, imsys_list = None, skip_duplicates = True):
        path = listoftype(path, str)
        if path is None:
            return self
        if imsys_list is None:
            imsys_list = globals()['template_dict'].keys()
        errors = []
        for path2scene in path:
            file = os.path.isfile(path2scene)
            if file:
                try:
                    fin = False
                    for imsys in imsys_list:
                        if fin:
                            break
                        templates = globals()['template_dict'].get(imsys)
                        if templates is not None:
                            for template in templates:
                                file = os.path.basename(path2scene)
                                if re.search(template, file):
                                    self.add_scene(path2scene, imsys, skip_duplicates=skip_duplicates)
                                    fin = True
                                    break
                except:
                    print('Error making scene: %s' % path2scene)
                    errors.append(path2scene)
            else:
                input_list = walk_find(path2scene, globals()['template_dict'].keys(), globals()['template_dict'].values())
                if (input_list is not None) and len(input_list)>0:

                    for newpath2scene in input_list:

                        newpath, imsys = newpath2scene

                        if 'new_KV' in newpath:
                            continue

                        # Filter scenes by imsys
                        if imsys not in imsys_list:
                            continue

                        try:
                            self.add_scene(newpath, imsys, skip_duplicates=skip_duplicates)
                        except:
                            print('Error making scene from list: %s' % newpath)
                            # self.add_scene(newpath, imsys, skip_duplicates=skip_duplicates)
                            errors.append(newpath)

        if len(errors) > 0:
            log = tempname('txt').replace('.txt', 'log_input.txt')
            with open(log, 'w') as txt:
                txt.write('\n'.join(errors))
            print('List of errors in %s' % log)

        return self

    # Get list of scene_ids
    def get_ids(self):
        ids_list = []
        for ascene in self.scenes:
            ids_list.append(ascene.meta.id)
        return ids_list

    # Get scene by id
    def get_scene(self, scene_id):
        for ascene in self.scenes:
            if ascene.meta.id == scene_id:
                return ascene
        return None

    # Delete scene by id
    def del_scene(self, scene_id):
        for i, ascene in enumerate(self.scenes):
            if ascene.meta.id == scene_id:
                self.scenes.pop(i)
                break
        return self

    def get_vector_cover(self, vector_cover_name, report_name=None):

        path2vector_list = []
        report = OrderedDict()

        for ascene in self.scenes:
            path2vector_list.append(fullpath(ascene.path, ascene.meta.datamask))
            rep_row = OrderedDict()
            rep_row['datamask'] = path2vector_list[-1]
            report[ascene.meta.id] = rep_row

        if report_name is not None:
            try:
                dict_to_xls(fullpath(self.output_path, report_name), report)
            except:
                print('Unable to export data as xls')
        geodata.JoinShapesByAttributes(path2vector_list, fullpath(self.output_path, vector_cover_name), geom_rule=1, attr_rule=0)

        return None

    # Returns json cover with standard set of fields from scenes metadata
    def GetCoverJSON(self, vector_cover_path, epsg=4326, add_path=True, cartezian_area = False, data_mask=False):

        fields_dict = globals()['geodata'].fields_dict

        driver = geodata.ogr.GetDriverByName('GeoJSON')
        ds_out = driver.CreateDataSource(vector_cover_path)

        if epsg is not None:
            srs = geodata.osr.SpatialReference()
            srs.ImportFromEPSG(epsg)
        else:
            srs = None

        lyr_out = ds_out.CreateLayer('', srs, geodata.ogr.wkbMultiPolygon)

        for field_id in fields_dict:
            if field_id=='path' and not add_path:
                continue
            field_params = fields_dict[field_id]
            field_defn = geodata.ogr.FieldDefn(field_id, field_params['type_id'])
            lyr_out.CreateField(field_defn)

        lyr_defn = lyr_out.GetLayerDefn()

        if len(self)>0:
            errors = []
            for ascene in self.scenes:
                try:
                    feat = ascene.json_feat(lyr_defn, add_path=add_path, cartesian_area=cartezian_area, data_mask=data_mask)
                    lyr_out.CreateFeature(feat)
                except Exception as e:
                    print('Error writing metadata %s from %s' % (str(e), ascene.path))
                    errors.append('%s from %s' % (str(e), ascene.path))
            if len(errors) > 0:
                log = tempname('txt').replace('.txt', 'log_cover.txt')
                with open(log, 'w') as txt:
                    txt.write('\n'.join(errors))
                print('List of errors in %s' % log)
        ds_out = None

        return 0

# Every space image scene
class scene:

    def __init__(self, path, imsys):

        if not os.path.exists(path):
            print('Path does not exist: "{}"'.format(path))
            raise IOError

        module = globals()['metalib'].get(imsys)
        if module is None:
            print('Unknown data source: {}'.format(imsys))
            raise KeyError

        meta = module.metadata(path)

        if not meta.check():
            raise ImportError

        self.fullpath = path
        folder, file = os.path.split(path)
        self.path = self.filepath = folder

        self.meta = meta

        self.file = file
        self.files = self.meta.files
        self.imsys = imsys
        self.clip_parameters = {}

        self.products = {}

    def __bool__(self):
        return bool(self.fullpath)

    # Get raster path by file id. Clip raster file if necessary
    def get_raster_path(self, file_id):

        file_id = str(file_id)

        if not file_id in self.files:
            if file_id in self.meta.files:
                path2file = self.clipraster(file_id)
            else:
                print('Unknown file id: {}'.format(file_id))
                return None
        else:
            path2file = fullpath(self.filepath, self.meta.get_raster_path(file_id))

        return path2file

    # Clips a single raster
    def clipraster(self, file_id):

        file_id = str(file_id)
        full_export_path = self.get_raster_local_path(file_id)
        export_folder = os.path.split(full_export_path)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        geodata.clip_raster(path2raster = fullpath(self.path, self.meta.get_raster_path(file_id)),
                            path2vector = self.clip_parameters.get('path2vector'),
                            export_path = full_export_path,
                            byfeatures = self.clip_parameters.get('byfeatures', True),
                            exclude = self.clip_parameters.get('exclude', False),
                            nodata = self.clip_parameters.get('nodata', 0),
                            compress = self.clip_parameters.get('compress'))

        self.files.append(file_id)

        return full_export_path

    # Gets path to raster file containing th bands and its number
    def get_band_path(self, band_id):

        band_id = str(band_id)
        band_tuple = self.meta.bandpaths.get(band_id)
        if band_tuple is not None:
            raster_path = self.get_raster_path(band_tuple[0])
        else:
            print('Unknown band_id: {}'.format(band_id))
            return None
        if raster_path is not None:
            return (raster_path, band_tuple[1])

        return (raster_path, band_tuple[1])

    def get_product_path(self, prod_id, band_id, set_product_path = None, set_name = None):

        if prod_id not in globals()['product_types_list']:
            print('Unknown product type: {}'.format(prod_id))
            return None

        if prod_id not in self.products:
            self.products[prod_id] = {}

        if band_id in self.products[prod_id]:

            prod_name, prod_bandnum =  self.products[prod_id][band_id]
            prod_path = (r'{}\{}'.format(set_product_path, prod_name))

        else:

            prod_func = get_product_generation_function(self.imsys, prod_id)

            if prod_func is None:
                return None

            if set_product_path is None:
                set_product_path = globals()['temp_dir_list_ip'].create()

            if set_name is None:
                prod_name = r'[id]_{}_{}.tif'.format(band_id, prod_id)
            else:
                prod_name = set_name

            prod_name = self.meta.name(prod_name)
            prod_path = (r'{}\{}'.format(set_product_path, prod_name))
            prod_bandnum = 1

            prod_func(self.get_band_path(band_id), band_id, (prod_path, prod_bandnum), self.meta, dt = globals()['raster_product_types'].get(prod_id))

            self.products[prod_id][band_id] = (prod_name, prod_bandnum)

        return (prod_path, prod_bandnum)

    # Creates a copy of a scene, cropping the original data with shpapefile
    def clip(self, path2vector, export_path = None, byfeatures = True, exclude = False, nodata = 0, save_files = False, compress = None):

        if export_path is None:
            export_path = temp_dir_list_ip.create()

        self.filepath = export_path
        self.files = []
        self.clip_parameters['path2vector'] = path2vector
        self.clip_parameters['byfeatures'] = byfeatures
        self.clip_parameters['exclude'] = exclude
        self.clip_parameters['nodata'] = nodata
        self.clip_parameters['compress'] = compress

        if save_files:
            for key in self.meta.filepaths:
                self.clipraster(key)

        return None

    # Aborts clipping scene, the created files aren't deleted
    def unclip(self):
        self.filepath = self.path
        self.filenames = self.meta.filenames
        self.clip_parameters = {}
        return None

    def datamask(self):
        if self.meta.datamask is not None:
            if self.imsys in ('DG', 'PLN'):
                return self.meta.datamask
            else:
                return fullpath(self.path, self.meta.datamask)
        else:
            return None

    # Returns a scene cover as a feature with standard set of attributes
    def json_feat(self, lyr_defn, add_path=True, cartesian_area = False, data_mask=False, srs=4326):
        feat = geodata.ogr.Feature(lyr_defn)
        # print(self.meta.id, self.datamask())
        ds_mask, lyr_mask = geodata.get_lyr_by_path(self.datamask())
        t_crs = geodata.get_srs(srs)
        if lyr_mask is not None:
            geom_feat = lyr_mask.GetNextFeature()
            geom = geom_feat.GetGeometryRef()
            # print(geom.ExportToWkt())
            v_crs = lyr_mask.GetSpatialRef()
            if (v_crs is None) and self.imsys=='PLD':
                v_crs = geodata.osr.SpatialReference()
                v_crs.ImportFromEPSG(4326)
                geom = geodata.MultipolygonFromMeta(self.fullpath, v_crs)
            else:
                if not geodata.ds_match(v_crs, t_crs):
                    # print(v_crs)
                    # print(t_crs)
                    coordTrans = geodata.osr.CoordinateTransformation(v_crs, t_crs)
                    geom.Transform(coordTrans)
                if sys.version.startswith('3'):
                    geom = geodata.changeXY(geom)
            feat.SetGeometry(geom)
        feat = globals()['metalib'].get(self.imsys).set_cover_meta(feat, self.meta)
        if self.imsys=='KAN' and 'NP' in self.meta.id:
            for type in ('mul', 'pan'):
                if type in self.meta.files:
                    mykanopus.meta_from_raster(feat, self.get_raster_path(type))
        elif self.imsys=='SS':
            myskysat.meta_from_raster(feat, self.get_raster_path('Analytic'))
        if add_path:
            feat.SetField('path', self.fullpath)
        if cartesian_area or data_mask:
            path2export = tempname('shp')
            if isinstance(self.meta.base, list):
                area = 0.0
                cover_list = []
                for base in self.meta.base:
                    if cartesian_area:
                        area += geodata.RasterDataCartesianArea(self.get_raster_path(base))
                    if data_mask:
                        temp_cover = tempname('shp')
                        geodata.RasterDataMask(self.get_raster_path(base), temp_cover, use_nodata=True, enforce_nodata=None, alpha=None,
                                               epsg=srs, overwrite=True)
                        cover_list.append(temp_cover)
            else:
                if cartesian_area:
                    area = geodata.RasterDataCartesianArea(self.get_raster_path(self.meta.base))
                if data_mask:
                    geodata.RasterDataMask(self.get_raster_path(self.meta.base), path2export, use_nodata=True,
                                       enforce_nodata=None, alpha=None, epsg=srs, overwrite=True)
            if cartesian_area:
                feat.SetField('area', area)
            if data_mask:
                new_ds, new_lyr = geodata.get_lyr_by_path(path2export)
                new_feat = new_lyr.GetNextFeature()
                new_geom = new_feat.GetGeometryRef()
                feat.SetGeometry(new_geom)
        return feat

    def quicklook(self):
        if self.meta.quicklook is not None:
            return fullpath(self.path, self.meta.quicklook)
        else:
            return None

    # Creates a composite of a single scene --- change
    def composite(self, bands, export_path, path2target = None, exclude_nodata = True, enforce_nodata = None, compress = None, overwrite = True):

        bandpaths = []
        for band_id in bands:
            bandpaths.append(self.get_band_path(band_id))

        try:
            res = geodata.raster2raster(bandpaths, export_path, path2target = path2target, exclude_nodata = exclude_nodata, enforce_nodata = enforce_nodata, compress = compress, overwrite=overwrite)
        except:
            print('Error making composite for: {}'.format(export_path))
            return 1

        return res

    # Creates default composite by name ('RGB', 'NIR', etc.)
    def default_composite(self, comptype, export_path, path2target = None, exclude_nodata = True, enforce_nodata = None, compress = None, overwrite = True):

        compdict = globals()['composites_dict']

        if comptype in compdict:
            # self.composite(compdict[comptype], export_path, path2target=path2target, exclude_nodata=exclude_nodata, enforce_nodata=enforce_nodata, compress = compress)
            try:
                res = self.composite(compdict[comptype], export_path, path2target=path2target, exclude_nodata=exclude_nodata, enforce_nodata=enforce_nodata, compress = compress, overwrite=overwrite)
                if res == 0:
                    print('{} composite saved: {}'.format(comptype, export_path))
                return res
            except:
                print('Cannot make composite: {} for scene {}'.format(comptype, self.meta.id))
                return 1
        else:
            print('Unknown composite: {}'.format(comptype))
            return 1

    # Calculates index by id
    def calculate_index(self, index_id, export_path, name = None, compress = None, overwrite = True):

        index_params = globals()['index_dict'].get(index_id)

        if index_params is not None:
            funcid, bandlist, dt, prod_id = index_params
            func = geodata.index_calculator.get(funcid)
            bandpath_list = []

            for band_id in bandlist:
                # bandpath_list.append(self.get_band_path(band_id))
                bandpath_list.append(self.get_product_path(prod_id, band_id, set_product_path=os.path.split(export_path)[0], set_name=name))

            if (func is not None) and (not None in bandpath_list):
                #func(bandpath_list, export_path, dt=dt)
                try:
                    res = func(bandpath_list, export_path, dt=dt, compress = compress, overwrite=overwrite)
                    if res == 0:
                        print('Index raster file saved: {}'.format(export_path))
                    return res
                except:
                    print('Error calculating {} to {}'.format(index_id, export_path))
                    res = func(bandpath_list, export_path, dt=dt, compress=compress, overwrite=overwrite)
                    return 1
            else:
                print('Insuffisient parameters for {} calculation'.format(index_id))
                return 1
