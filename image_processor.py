# -*- coding: utf-8 -*-

# Version 0.3

from tools import *

import geodata

# import mylandsat
import myplanet
import mykanopus
import mysentinel
import myresursp
import mydg
import myskysat

# Constants

default_output = os.getcwd() # default output directory for a process

metalib = {
    # 'LST': mylandsat,
    'SNT': mysentinel,
    'PLN': myplanet,
    'KAN': mykanopus,
    'RSP': myresursp,
    'DG': mydg,
    'SS': myskysat,
}

# A dictionary of metadata filenames templates
template_dict = {}
for key in metalib:
    template_dict[key] = metalib[key].templates

'''
template_dict = {
    imsys1_name: (template1, template2, ),
    imsys2_name: (template1, template2, template3, ),
    ... etc. ...
}
'''

#scroll(template_dict)

'''
-- keeping here until new modules will be made

# Set image systems available for analysis
image_system_list = [
    'LST',                  # LANDSAT
    'SNT',                  # SENTINEL
    'PLN',                  # PLANET
    'KAN',                  # KANOPUS
]

# Set spacecraft list
spacecraft_list = [
    'LS8',                  # LANDSAT-8
    'SN2',                  # SENTINEL-2A
    'S2B',                  # SENTINEL-2B
    'PLN',                  # PLANET
]

# Templates for searching metadata files
corner_file_list = {                                # Helps to find metadata files
            'Landsat-8':    r'L[CE]\d\d_.+_MTL\.txt',
            'Sentinel-2':   r'MTD_MSIL\d[CA]\.xml',
            'Planet':       r'\d+_\d+_\S+_Analytic\S*_metadata.xml',
        }


# Set indexes for different channels in different image systems 
# Landsat-8
band_dict_lsat8 = {
    'coastal': '1',
    'blue': '2',
    'green': '3',
    'red': '4',
    'nir': '5',
    'swir1': '6',
    'swir2': '7',
    'pan': '8',
    'cirrus': '9',
    'tirs1': '10',
    'tirs2': '11'
}

'''

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

# Defines image system by path to file or returns None if no one matches
def get_imsys(path):
    if os.path.exists(path):
        for imsys, module in globals()['metalib']:
            file = os.path.split(path)[1]
            if check_name(file, module.template):
                return imsys
    else:
        print('Path does not exist: {}'.format(path))
    return None

# Returns product generation function
def get_product_generation_function(imsys, prodid):

    func = globals()['metalib'].get(imsys).product_func.get(prodid)

    if hasattr(func, '__repr__'):
        return func

    else:
        print('"{}" product function not found for "{}"'.format(prodid, imsys))
        return None

temp_dir_list = tdir(default_temp) # tdir object for working with temporary files

# Class containing image processing parameters and procedures
class process(object):

    def __init__(self,
                 output_path=globals()['default_output'],
                 #image_system = globals()['image_system_list'],
                 #work_method = globals()['work_method_list'][0],
                 tdir = globals()['default_temp']):

        self.output_path = output_path  # must be dir
        #self.work_method = work_method
        #self.input = []
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
    def add_scene(self, newpath, imsys):
        newscene = scene(newpath, imsys)
        # print(newpath)
        try:
            newscene = scene(newpath, imsys)
        #except FileNotFoundError:
        except:
            print('Cannot open {} scene by path: {}'.format(imsys, newpath))
            newscene = None
        if newscene is not None:
            self.scenes.append(newscene)
        return self

    def input(self, path, imsys_list = None):
        path = listoftype(path, str)
        # print('Path: {}'.format(path))
        if path is None:
            return self
        if imsys_list is None:
            imsys_list = globals()['template_dict'].keys()
        # print(imsys_list)
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
                        # print(templates)
                        if templates is not None:
                            for template in templates:
                                # print(template)
                                if re.search(template, path2scene) is not None:
                                    # print(re.search(template, path2scene).group())
                                    self.add_scene(path2scene, imsys)
                                    fin = True
                                    break
                except:
                    print('Error making scene: %s' % path2scene)
                    errors.append(path2scene)
            else:
                input_list = walk_find(path2scene, globals()['template_dict'].keys(), globals()['template_dict'].values())
                # scroll('Input list: {}'.format(input_list))
                if (input_list is not None) and len(input_list)>0:

                    for newpath2scene in input_list:
                        # print(newpath2scene)
                        newpath, imsys = newpath2scene

                        # Filter scenes by imsys
                        if imsys not in imsys_list:
                            continue

                        try:
                            self.add_scene(newpath, imsys)
                        except:
                            # self.add_scene(newpath, imsys)
                            print('Error making scene: %s' % newpath)
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

    # Filters scenes by id values
    def filter_ids(self, id_part_dict):
        proc_new = process()
        for id in self.get_ids():
            for id_part in id_part_dict:
                if id_part in id:
                    proc_new.input(self.get_scene(id).fullpath)
                    break
        return proc_new

    # Get scene by id
    def get_scene(self, scene_id):
        for ascene in self.scenes:
            if ascene.meta.id == scene_id:
                return ascene
        # print('Scene not found: {}'.format(scene_id))
        return None

    # Delete scene by id
    def del_scene(self, scene_id):
        for i, ascene in enumerate(self.scenes):
            if ascene.meta.id == scene_id:
                self.scenes.pop(i)
                break
        return self

    def get_dates(self):
        dates_list = []
        for ascene in self.scenes:
            # print(ascene.meta.datetime.date())
            scene_date = ascene.meta.datetime.date()
            if scene_date not in dates_list:
                dates_list.append(scene_date)
        dates_list.sort()
        return dates_list

    def get_paths(self):
        paths_dict = OrderedDict()
        for ascene in self.scenes:
            paths_dict[ascene.meta.id] = ascene.path
        return paths_dict

    # Returns a dictionary of scene covers shapefiles list
    def get_cover_paths(self):
        covers_dict = OrderedDict()
        for ascene in self.scenes:
            datamask = ascene.datamask()
            if datamask is not None:
                covers_dict[ascene.meta.id] =  fullpath(ascene.path, datamask)
            else:
                print('Datamask not found for {}'.format(ascene.meta.id))
        return covers_dict

    def get_vector_cover(self, vector_cover_name, report_name=None):

        path2vector_list = []
        report = OrderedDict()

        for ascene in self.scenes:
            # print(ascene.meta.datamask)
            path2vector_list.append(fullpath(ascene.path, ascene.meta.datamask))
            # path2vector_list.append(ascene.meta.datamask)
            rep_row = OrderedDict()
            rep_row['datamask'] = path2vector_list[-1]
            report[ascene.meta.id] = rep_row

        if report_name is not None:
            try:
                dict_to_xls(fullpath(self.output_path, report_name), report)
            except:
                print('Unable to export data as xls')
                # scroll(report)
        # print(fullpath(self.output_path, vector_cover_name))
        geodata.JoinShapesByAttributes(path2vector_list, fullpath(self.output_path, vector_cover_name), geom_rule=1, attr_rule=0)

        return None

    def get_json_cover(self, vector_cover_path):

        fields_dict = OrderedDict()
        fields_dict['id'] = {'type_id': 4}
        fields_dict['id_s'] = {'type_id': 4}
        fields_dict['id_neuro'] = {'type_id': 4}
        fields_dict['datetime'] = {'type_id': 4}
        fields_dict['clouds'] = {'type_id': 2}
        fields_dict['sun_elev'] = {'type_id': 2}
        fields_dict['sun_azim'] = {'type_id': 2}
        fields_dict['sat_id'] = {'type_id': 4}
        fields_dict['sat_view'] = {'type_id': 2}
        fields_dict['sat_azim'] = {'type_id': 2}
        fields_dict['channels'] = {'type_id': 0}
        fields_dict['type'] = {'type_id': 4}
        fields_dict['format'] = {'type_id': 4}
        fields_dict['rows'] = {'type_id': 0}
        fields_dict['cols'] = {'type_id': 0}
        fields_dict['epsg_dat'] = {'type_id': 0}
        fields_dict['u_size'] = {'type_id': 0}
        fields_dict['x_size'] = {'type_id': 2}
        fields_dict['y_size'] = {'type_id': 2}
        fields_dict['level'] = {'type_id': 4}
        fields_dict['area'] = {'type_id': 2}
        fields_dict['path'] = {'type_id': 4}

        geodata.json_fields(vector_cover_path, geodata.ogr.wkbMultiPolygon, 4326, fields_dict)
        ds_out, lyr_out = geodata.get_lyr_by_path(vector_cover_path, True)


    def get_vector_cover_json(self, vector_cover_path, attributes = []):

        ds_out = geodata.json(vector_cover_path, editable=True)
        lyr_out = ds_out.GetLayer()
        for fieldid in attributes:
            lyr_out.CreateField(geodata.ogr.FieldDefn(fieldid, 4))
        ds_out = None

        ds_out, lyr_out = geodata.get_lyr_by_path(vector_cover_path, editable = True)

        for ascene in self.scenes:

            try:

                ds_in, lyr_in = geodata.get_lyr_by_path(ascene.datamask())

                for fieldid in attributes:
                    lyr_in.CreateField(geodata.ogr.FieldDefn(fieldid, 4))

                if lyr_in is None:
                    print('Datamask not found for: {}'.format(ascene.meta.id))
                else:
                    lyr_in.ResetReading()
                    for feat_in in lyr_in:
                        # feat_out = geodata.feature(feature_defn = None, geom = feat_in, attr = None, attr_type = 0, attr_type_dict = {}, ID = None)
                        # feat_out = copy(feat_in)
                        feat_out_defn = feat_in.GetDefnRef()
                        for fieldid in attributes:
                            feat_out_defn.AddFieldDefn(geodata.ogr.FieldDefn(fieldid, 4))
                        feat_out = geodata.feature(feature_defn = feat_out_defn, geom = feat_in.GetGeomRef(), attr = None, attr_type = 0, attr_type_dict = {}, ID = None)
                        for fieldid in attributes:
                            feat_out.SetField(fieldid, ascene.meta.name('[{}]'.format(fieldid)))
                        print(feat_out.keys())
                        lyr_out.CreateFeature(feat_out)

            except:

                print('Error getting vector cover for: {}'.format(ascene.meta.id))

                ds_in, lyr_in = geodata.get_lyr_by_path(ascene.datamask())

                for fieldid in attributes:
                    lyr_in.CreateField(geodata.ogr.FieldDefn(fieldid, 4))

                if lyr_in is None:
                    print('Datamask not found for: {}'.format(ascene.meta.id))
                else:
                    lyr_in.ResetReading()
                    for feat_in in lyr_in:
                        # feat_out = geodata.feature(feature_defn = None, geom = feat_in, attr = None, attr_type = 0, attr_type_dict = {}, ID = None)
                        # feat_out = copy(feat_in)
                        feat_out_defn = feat_in.GetDefnRef()
                        for fieldid in attributes:
                            feat_out_defn.AddFieldDefn(geodata.ogr.FieldDefn(fieldid, 4))
                        feat_out = geodata.feature(feature_defn=feat_out_defn, geom=feat_in.GetGeometryRef(), attr=None,
                                                   attr_type=0, attr_type_dict={}, ID=None)
                        for fieldid in attributes:
                            feat_out.SetField(fieldid, ascene.meta.name('[{}]'.format(fieldid)))
                        print(feat_out.keys())
                        lyr_out.CreateFeature(feat_out)

        ds_out = None

        return 0

    # Returns json cover with standard set of fields from scenes metadata
    def GetCoverJSON(self, vector_cover_path, epsg=4326, add_path=True, data_mask=False):

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
                    feat = ascene.json_feat(lyr_defn, add_path=add_path, data_mask=data_mask)
                    lyr_out.CreateFeature(feat)
                    # print('Metadata written: {}'.format(ascene.meta.id))
                except:
                    feat = ascene.json_feat(lyr_defn, add_path=add_path, data_mask=data_mask)
                    lyr_out.CreateFeature(feat)
                    print('Error writing metadata: %s' % ascene.path)
                    errors.append(ascene.path)
            if len(errors) > 0:
                log = tempname('txt').replace('.txt', 'log_cover.txt')
                with open(log, 'w') as txt:
                    txt.write('\n'.join(errors))
                print('List of errors in %s' % log)
        # print(len(lyr_out))
        # for feat in lyr_out: print(feat.GetGeometryRef().ExportToWkt())
        ds_out = None

        return 0

    def get_change(self, old_scene_id, new_scene_id, intersection_mask = None):

        old_scene = self.get_scene(old_scene_id)
        new_scene = self.get_scene(new_scene_id)

        if (old_scene is None) or (new_scene is None):
            print('Scenes not found for {} and {}'.format(old_scene_id, new_scene_id))
            return 1

        old_datamask = old_scene.meta.datamask
        new_datamask = new_scene.meta.datamask

        if intersection_mask is None:
            intersection_mask = tempname('json')

        if (old_datamask is not None) and (new_datamask is not None):
            pass



# Every space image scene
class scene:

    def __init__(self, path, imsys):

        if not os.path.exists(path):
            print('Path does not exist: "{}"'.format(path))
            # raise FileNotFoundError
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
                set_product_path = globals()['temp_dir_list'].create()
                print(set_product_path)

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
            export_path = temp_dir_list.create()

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
            if self.imsys in ('DG'):
                return self.meta.datamask
            else:
                return fullpath(self.path, self.meta.datamask)
        else:
            return None

    # Returns a scene cover as a feature with standard set of attributes
    def json_feat(self, lyr_defn, add_path=True, data_mask=False, srs=4326):
        feat = geodata.ogr.Feature(lyr_defn)
        ds_mask, lyr_mask = geodata.get_lyr_by_path(self.datamask())
        if lyr_mask is not None:
            geom_feat = lyr_mask.GetNextFeature()
            geom = geom_feat.GetGeometryRef()
            feat.SetGeometry(geom)
        feat = globals()['metalib'].get(self.imsys).set_cover_meta(feat, self.meta)
        if self.imsys=='KAN' and 'NP' in self.meta.id:
            for type in ('mul', 'pan'):
                if type in self.meta.files:
                    mykanopus.meta_from_raster(feat, self.get_raster_path(type))
        elif self.imsys=='SS':
            myskysat.meta_from_raster(feat, self.get_raster_path('Analytic'))
        if add_path:
            feat.SetField('path', self.path)
        if data_mask:
            path2export = tempname('shp')
            if isinstance(self.meta.base, list):
                cover_list = []
                for base in self.meta.base:
                    temp_cover = tempname('shp')
                    geodata.RasterDataMask(base, temp_cover, use_nodata=True, enforce_nodata=None, alpha=None, epsg=srs, overwrite=True)
                    cover_list.append(temp_cover)
                geodata.Unite(cover_list, path2export, proj=None, deafault_srs=srs, overwrite=True)
            else:
                geodata.RasterDataMask(self.get_raster_path(self.meta.base), path2export, use_nodata=True, enforce_nodata=None, alpha=None, epsg=srs, overwrite=True)
            # print(path2export)
            new_ds, new_lyr = geodata.get_lyr_by_path(path2export)
            new_feat = new_lyr.GetNextFeature()
            new_geom = new_feat.GetGeometryRef()
            # print(new_geom.ExportToWkt())
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

        # scroll(bandpaths)

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

def timecomposite(scenes, band_ids, scene_nums, export_path, path2target = None, exclude_nodata = True, compress = None):

    assert len(band_ids) == len(scene_nums)

    bandpaths = []
    for i, band_id in enumerate(band_ids):
        bandpaths.append(scenes[scene_nums[i]].get_band_path(band_id))
    # scroll(bandpaths)

    try:
        res = geodata.raster2raster(bandpaths, export_path, path2target = path2target, exclude_nodata = exclude_nodata, compress = compress)
        if res == 0:
            print('Time composite saved: {}'.format(export_path))
    except:
        print('Error saving timecomposite: {}'.format(export_path))
        return 1

    return res

# Лютая херня для RGBN
def RGBNref(ascene, folder):
    refpaths = []
    for band_id in ['red', 'green', 'blue', 'nir']:
        refpaths.append(ascene.get_product_path('Reflectance', band_id, set_product_path=folder, set_name='{}-[fullsat]-[date]-[location]-[lvl].tif'.format(band_id.upper())))
    # path2export = fullpath(folder, ascene.meta.name(r'RF4-[fullsat]-[date]-[location]-[lvl].tif'))
    path2export = fullpath(folder, globals()['temp_dir_list'].create('tif'))
    geodata.raster2raster(refpaths, path2export, path2target=None, method=geodata.gdal.GRA_NearestNeighbour, exclude_nodata=True, enforce_nodata=None, compress='LZW', overwrite=True)
    return None

# Deleting temporary files at the end of the program
def fin():
    globals()['temp_dir_list'].__del__()
    globals()['geodata'].temp_dir_list.__del__()

def SceneMarker():
    from PIL import Image
    import time
    proc = process()
    path = input('Write a path to scenes: ')
    proc.input(path)
    report = OrderedDict()
    print('Starting marking a set of %i scenes. Print "break" to stop it' % len(proc))
    for i, ascene in enumerate(proc.scenes):
        if (i+1)%20 == 0:
            print('over 20 quicklooks are now open, please close the windows')
            time.sleep(10)
        with Image.open(fullpath(ascene.path, ascene.meta.quicklook)) as quicklook:
            quicklook.show()
            mark = input(ascene.meta.name('Give a mark to scene [id]: '))
            if mark == 'break':
                break
            elif mark is not None:
                report[ascene.meta.id] = {'mark': mark}
    print('Finished marking, %i scenes have been marked' % len(report))
    xlspath = input('Write a path to xls report: ')
    if len(xlspath) > 0:
        try:
            dict_to_xls(xlspath, report)
        except:
            answer = None
            while (answer != 'y') and (answer != 'n'):
                answer = input('Error writing xls report, try to save it manually? (y/n)')
                if answer == 'y':
                    return report
                elif answer == 'n':
                    return None
    return report
