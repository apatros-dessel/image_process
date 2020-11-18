import os
import ogr
import osr
import csv
import numpy as np
import xlrd
import xlwt

np_text_types = ['<U3', 'O']

# Unites lists adding unique values
def unite_lists(list1, list2):
    for val in list2:
        if val not in list1:
            list1.append(val)
    return list1

# Returns maximum length of the list elements
def list_max_len(list_obj):
    l = 0
    for val in list_obj:
        if len(str(val)) > l:
            l = len(str(val))
    return l

# Returns maximum length of attributes columns
# Works only with vectors of shape = (1, n>=1)
def attr_len(attr_dict):
    assert isinstance(attr_dict, dict)
    length = 0
    for key in attr_dict:
        assert isinstance(attr_dict[key], np.ndarray)
        if length < attr_dict[key].shape[1]:
            length = attr_dict[key].shape[1]
    return length

# Returns a set of unique values of a dictionary of lists
def dict_keyval(attr_dict, i):
    assert isinstance(attr_dict, dict)
    export = {}
    for key in attr_dict:
        assert isinstance(attr_dict[key], list)
        try:
            export[key] = attr_dict[key][i]
        except IndexError:
            print("No data found for ['{}', {}]".format(key, i))
            export[key] = None
    return export

# Stretches an array up to necessary length
# Works only with vectors of shape = (1, n>=1)
def array_fill(array2add, length=0, deficit=None, filler=None):
    assert array2add.ndim==2 and array2add.shape[0]==1
    if not deficit:
        deficit = max([0, length - array2add.shape[1]])
    if deficit:
        array2add = np.hstack((array2add, np.full((1, deficit), filler, dtype=array2add.dtype)))
    return array2add

# Adds new column to the attribute dictionary
def add_constant_col(attr_dict, colname, value=0):
    if colname in attr_dict:
        print("Column already exists: %s" % colname)
    else:
        attr_dict[colname] = np.full((1, attr_len(attr_dict)), value)
    return attr_dict

# Assures that all columns in the attribute dictionary are of the same length
def dict_check(attr_dict, length = 0, filler_dict={}, nodata=0):
    if not length:
        length = attr_len(attr_dict)
    for key in attr_dict:
        filler = filler_dict.get(key, nodata)
        attr_dict[key] = array_fill(attr_dict[key], length=length, filler=filler)
    return attr_dict

# Assures correspondence between attribute list and attribute dictionary
def attr_check(attr_list, attr_dict, array=True, nodata=0):
    assert isinstance(attr_list, list)
    assert isinstance(attr_dict, dict)
    for key in attr_dict:
        if key not in attr_list:
            attr_list.append(key)
    length = attr_len(attr_dict)
    for attr_name in attr_list:
        if attr_name not in attr_dict:
            attr_dict[attr_name] = np.full((1,length), nodata)
    return attr_list, attr_dict

# Assures correspondence between wkt list and attribute dictionary
def wkt_check(wkt, attr_dict, nodata=0):
    assert isinstance(wkt, list)
    assert isinstance(attr_dict, dict)
    length = attr_len(attr_dict)
    if length > len(wkt):
        wkt = wkt + list(np.full(length - len(wkt), ''))
    elif len(wkt) > length:
        attr_dict = dict_check(attr_dict, length=len(wkt), nodata=nodata)
    return wkt, attr_dict

# Returns wkt point geometry
def wkt_point(x_coord, y_coord):
    return "POINT (%f %f)" % (x_coord, y_coord)

# Returns wkt linestring geometry
def wkt_polyline(x_coord, y_coord):
    assert len(x_coord) == len(y_coord)
    wkt = "LINESTRING ("
    for i in range(len(x_coord)):
        wkt += "%f %f, " % (x_coord[i], y_coord[i])
    wkt = wkt[:-2] + ")"
    return wkt

# Returns wkt polygon geometry
def wkt_polygon(coord_list):
    wkt = "POLYGON (("
    for i in range(len(coord_list)):
        assert len(coord_list[i][0]) == len(coord_list[i][1]) > 0
        for j in range(len(coord_list[i][0])):
            wkt += "%f %f, " % (coord_list[i][0][j], coord_list[i][1][j])
        if (coord_list[0][0][0] != coord_list[0][0][-1]) or (coord_list[0][1][0] != coord_list[0][1][-1]):
            wkt += "%f %f, " % (coord_list[i][0][0], coord_list[i][1][0])
        wkt = wkt[:-2] + "), ("
    wkt = wkt[:-3] + ")"
    return wkt

# Indexes an array
def index(array2index):
    assert isinstance(array2index, np.ndarray)
    vals = np.unique(array2index)
    range = np.arange(1, len(vals)+1)
    new_array = np.zeros(array2index.shape)
    val_dict = {}
    for num in range:
        val_dict[num] = vals[num-1]
        new_array[array2index==val_dict[num]] = num
    assert len(new_array[new_array==0])==0
    return new_array, val_dict

# Stacks multiple columns indexing them if necessary
def vstack_index(array_list, index_dtypes_list=globals()['np_text_types']):
    stack = []
    index_dict = {}
    for i in range(len(array_list)):
        if array_list[i].dtype in index_dtypes_list:
            indexed, ids = index(np.copy(array_list[i]))
            stack.append(indexed)
            index_dict[i] = ids
        else:
            stack.append(array_list[i])
    stacked = np.vstack(tuple(stack))
    return stacked, index_dict

# Matches the same numbers of arrays
# Rows 0 and 1 - matching values' indices, row 2 - if they match exactly, row 3 - if no other matches found
def pair_array(arr1, arr2):
    length = len(arr1)
    pairing = np.vstack((np.arange(length), np.zeros(3*length).reshape(3,length)))
    for i in range(len(arr1)):
        count_zero = np.sum(abs(arr2 - arr1[i]), axis=1)
        id2 = np.argsort(count_zero)[:2]
        pairing[1,i] = id2[0]
        pairing[2,i] = count_zero[id2[0]]
        pairing[3, i] = count_zero[id2[1]]
    pairing[2] = ~ pairing[2].astype(bool) # Shows that the min dist values're equal to zero
    pairing[3] = pairing[3].astype(bool) # Shows that other distances're greater than zero
    # The non-mathcing values are not filtered but the data is exported
    return pairing

wkt_fun_list = {
            'POINT':        wkt_point,
            'LINESTRING':   wkt_polyline,
            'POLYGON':      wkt_polygon,
        }

wkt2ogr = {
    'POINT':            ogr.wkbPoint,
    'LINESTRING':       ogr.wkbLineString,
    'POLYGON':          ogr.wkbPolygon,
    'MULTIPOINT':       ogr.wkbMultiPoint,
    'MULTILINESTRING':  ogr.wkbMultiLineString,
    'MULTIPOLYGON':     ogr.wkbMultiPolygon,
}

# Import shapefile to dict of arrays
def shp2dict(path2shp, import_wkt=False):
    shp_ds = ogr.Open(path2shp)
    if shp_ds is None:
        print('Cannot open dataset: {}'.format(path2shp))
        return None
    lyr = shp_ds.GetLayer()
    feat = lyr.GetNextFeature()
    gobj = feat2gobj(feat, import_wkt=import_wkt)
    add_dict = {}
    add_list = gobj.attr_list
    length = lyr.GetFeatureCount()
    for key in add_list:
        add_dict[key] = np.zeros((1, length), dtype=gobj.attr[key].dtype)
    if import_wkt:
        wkt = list(np.full(length), '')
    else:
        wkt = False
    for i in range(length):
        gobj = feat2gobj(feat, import_wkt=import_wkt)
        # self.add_geoobject(feat2gobj(feat, import_wkt=self.wkt))
        for key in gobj.attr_list:
            add_dict[key][0, i] = gobj.attr[key][0, 0]
        if import_wkt:
            wkt[i] = gobj.wkt
        feat = lyr.GetNextFeature()
    return add_dict, add_list, wkt

# Adds the fields to dataset from a list or 1-dim array
def dict2shp_points(filename, attr_dict, col_dict, width=None, epsg=4326, x_coord=None, y_coord=None):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(filename)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    lyr = data_source.CreateLayer('Layer', srs, ogr.wkbPoint)
    l = attr_len(attr_dict)
    for key in col_dict:
        if not key in attr_dict:
            raise Exception('No parameter %s found' % (key))
        dtype = col_dict[key]
        field = ogr.FieldDefn(key, dtype)
        if dtype == ogr.OFTString:
            if width is None:
                width = list_max_len(attr_dict[key])
            field.SetWidth(width)
        try:
            lyr.CreateField(field)
        except:
            print('Cannot create field %s' % key)
    for i in range(l):
        feat = ogr.Feature(lyr.GetLayerDefn())
        for key in col_dict:
            try:
                feat.SetField(key, attr_dict[key][0,i])
            except:
                print('Cannot set field %s' % key)
        if x_coord is not None and y_coord is not None:
            if (x_coord in attr_dict) and (y_coord in attr_dict):
                x = attr_dict[x_coord][0,i]
                y = attr_dict[y_coord][0,i]
                wkt = "POINT(%f %f)" % (np.single(x), np.single(y))
                point = ogr.CreateGeometryFromWkt(wkt)
                feat.SetGeometry(point)
        lyr.CreateFeature(feat)
        feat = None
    data_source = None
    return None

# Imports csv data to a dict of arrays
def csv2dict(path, names1st_line=True, delimeter=';', endline=','):
    if not os.path.exists(path):
        raise Exception('Path not found %s' % path)
    csvfile = csv.reader(open(path))
    read_list = []
    for line in csvfile:
        add_list = np.array(line[0].split(delimeter))
        for i in range(len(add_list)):
            add_list[i] = str(add_list[i]).strip()
        read_list.append(add_list)
    len_ = len(read_list[0])
    for line_list in read_list:
        if len(line_list) != len_:
            raise Exception(r"Number of columns doesn't match")
    if names1st_line:
        names_list = read_list[0]
        read_list = read_list[1:]
    else:
        names_list = []
        for num in range(len_):
            names_list.append('col_{}'.format(num))
    read_list = np.vstack(tuple(read_list))
    csvdata = {}
    for num in range(len_):
        col_name = ukey(names_list[num], csvdata.keys())
        csvdata[col_name] = read_list[:,num].reshape((1,len(read_list)))
    return csvdata, names_list

# Import data from xls
def xls2dict(path2xls, sheet_num=0, get_col_names=True, omit_first_col=False):
    rb = xlrd.open_workbook(path2xls)
    if rb.nsheets <= sheet_num:
        print('Warning: sheet_num exeeds number of sheets in the workbook')
        sheet_num = rb.nsheets - 1
    sheet = rb.sheet_by_index(sheet_num)
    xlsdict = {}
    for col_num in range(omit_first_col, sheet.ncols):
        col = sheet.col_values(col_num)
        if get_col_names:
            key = str(col[0])
        else:
            key = 'col_%i' % col_num
        key = ukey(key, xlsdict.keys())
        xlsdict[key] = np.array(col[get_col_names:])
    return xlsdict

# Returns unique key not existing in key_list
# Adds _%i if necessary
def ukey(key, key_list):
    if key in key_list:
        copy_num = 1
        while key in key_list:
            copy_num += 1
            newkey = '{}_{}'.format(key, copy_num)
    else:
        newkey = key
    return key

# Calculates decimal degrees coordinates from degree-minutes-seconds given as arrays of shape (1,m)
def decimal_deg(deg=None, min=None, sec=None):
    if (deg is None) and (min is None) and (sec is None):
        print('No data found, cannot calculate coordinates')
        return None
    coord_dict = { 'deg': deg, 'min': min, 'sec': sec}
    for key in coord_dict:
        if coord_dict[key] is None:
            coord_dict[key] = np.array([0]).reshape((1,1))
    coord_dict = dict_check(coord_dict)
    DD = coord_dict['deg'] + coord_dict['min']/60 + coord_dict['sec']/3600
    return DD

# Contains geoattribute data in form of (1,n)-shaped arrays
class geoarray:

    def __init__(self, wkt = False, attr_list = [], attr_dict={}, descript = '', geomtype=None, nodata={}):
        attr_dict = dict_check(attr_dict, nodata=nodata)
        self.attr_list, attr_dict = attr_check(attr_list, attr_dict, nodata=nodata)
        if wkt:
            self.wkt, self.attr = wkt_check(wkt, attr_dict, nodata=nodata)
        else:
            self.wkt = wkt
            self.attr = attr_dict
        self.descript = descript
        self.length = attr_len(attr_dict)
        self.width = len(self.attr_list)
        self.nodata = nodata
        self.geomtype = geomtype

    # Number of objects
    def __len__(self):
        return self.length

    def __str__(self):
        return 'gattr object of length %i' % self.length

    # If gattr object contains any
    def __bool__(self):
        return self.length > 0

    # Get a single object, an attribute column or a specified attribute value for a specified object
    def __getitem__(self, item):
        if item is None:
            return None
        elif isinstance(item, int):
            return self.get_geoobject(item)
        elif isinstance(item, str):
            return self.get_attribute(item)
        elif isinstance(item, (tuple, list)):
            if len(item)==2:
                # The first value is expected to be an attribute name and the second one should be a feature number
                return self.get_attribute(item[0])[0,item[1]]
        raise KeyError('Unacceptable key type: integer or list or tuple of len 2 is required')

    # Returns geoobject by value
    def get_geoobject(self, i):
        attr = dict_keyval(self.attr, i)
        if self.wkt:
            wkt = self.wkt[i]
        else:
            wkt = ''
        return geoobject(wkt = wkt, attr_list = self.attr_list, attr = attr)

    def get_attribute(self, key):
        if key in self.attr:
            return self.attr[key]
        else:
            raise KeyError('No attribute found: %s' % key)

    # Write data on a single object to the gattr
    def add_geoobject(self, gobj):
        assert isinstance(gobj, geoobject)
        self.add_strings(gobj.attr)
        self.attr_list, self.attr = attr_check(self.attr_list, self.attr, nodata=self.nodata)
        if self.wkt:
            self.wkt[-1] = gobj.wkt
        return self

    # Adds attributes from a dictionary of arrays
    def add_strings(self, dict2add, nodata=0):
        dict2add = dict_check(dict2add, filler_dict=self.nodata)
        length = attr_len(dict2add)
        for key in dict2add:
            if key in self.attr_list:
                self.attr[key] = np.hstack((self.attr[key], dict2add[key]))
        for key in self.attr_list:
            if key not in dict2add:
                filler = self.nodata.get(key, nodata)
                self.attr[key] = np.hstack((self.attr[key], np.full((1,length), filler)))
        if self.wkt:
            self.wkt, self.attr = wkt_check(self.wkt, self.attr, nodata=nodata)
        self.length = attr_len(self.attr)
        return self

    # Adds a new column to the geoarray
    def add_column(self, key, vector):
        assert isinstance(key, str) and isinstance(vector, np.ndarray)
        assert vector.shape == (1, self.length)
        if key in self.attr_list:
            raise KeyError('The column already exists: %s' % key)
        self.attr_list.append(key)
        self.attr[key] = vector
        self.width = len(self.attr)
        return None

    def rename_column(self, oldname, newname):
        if oldname in self.attr_list:
            self.attr_list[self.attr_list.index(oldname)] = newname
            self.attr[newname] = self.attr[oldname]
            self.attr.pop(oldname)
        else:
            raise KeyError("Column not found: {}".format(oldname))
        return self

    # Assures correspondence between attribute dictionary and attribute list
    def check(self):
        self.attr_list, self.attr = attr_check(self.attr_list, self.attr, nodata=self.nodata)
        return self

    # Adds wkt points from the columns on specified positions
    def set_wkt_points(self, x_col, y_col, save_wkt=True):
        coord = {'x_col': x_col, 'y_col': y_col}
        for i in ['x_col', 'y_col']:
            if coord[i] not in self.attr_list:
                raise KeyError('No column found: %s' % x_col)
        wkt_list = []
        for i in range(self.length):
            wkt_list.append(wkt_point(self[x_col][0][i], self[y_col][0][i]))
        if save_wkt:
            self.wkt = wkt_list
        return wkt_list

    def set_descript(self, descr):
        self.descript = str(descr)
        return self.descript

    def add_descript(self, descr):
        self.descript += '\n '.format(descr)
        return self.descript

    '''
    def set_wkt_objects(self, wkt_type, x_col, y_col, obj_col, sort_col, save_wkt=False):
        obj_list = np.unique(self[obj_col])
        if wkt_type in globals()['wkt_fun_list']:
            wkt_fun = globals()['wkt_fun_list'][wkt_type]
        else:
            raise KeyError("Unknown wkt type: {}".format(wkt_type))
        order = np.argsort(sort_col)
        x_coords = self[x_col][order]
        y_coords = self[y_col][order]
        wkt_list = []
        for key in obj_list:
            mask = self[obj_col][self[obj_col]==key]
            wkt_obj = wkt_fun(x_coords[mask], y_coords[mask])
            wkt_list.append(wkt_obj)
            if save_wkt:
                self.wkt = list(np.full(self.length, ''))
        return wkt_list
    '''

    def set_wkt_polylines(self, x_col, y_col, obj_col, sort_col):
        obj_list = np.unique(self[obj_col])
        order = np.argsort(sort_col)
        x_coords = self[x_col][0][order]
        y_coords = self[y_col][0][order]
        wkt_list = []
        for key in obj_list:
            mask = self[obj_col][self[obj_col] == key]
            wkt_obj = wkt_polyline(x_coords[mask], y_coords[mask])
            wkt_list.append(wkt_obj)
            if self.wkt:
                for i in order[mask]:
                    self.wkt[i] = wkt_obj
        return wkt_list

    def set_wkt_polygons(self, x_col, y_col, obj_col, sort_col, part_col):
        obj_list = np.unique(self[obj_col])
        part_list = np.unique(part_col)
        order = np.argsort(sort_col)
        x_coords = self[x_col][0][order]
        y_coords = self[y_col][0][order]
        polygon_gar = geoarray(geomtype='POLYGON')
        for key in obj_list:
            mask = self[obj_col][0] == key
            coord_list = []
            for part_key in part_list:
                part_mask = self[part_col][0][mask] == part_key
                coord_list.append((x_coords[part_mask], y_coords[part_mask]))
            wkt = wkt_polygon(coord_list)
            attr = {'obj_col': key}
            polygon_gobj = geoobject(wkt=wkt, attr=attr)
            polygon_gar.add_geoobject(polygon_gobj)
        return polygon_gar

    # Import data from shapefile
    def import_from_shp(self, path2shp, filename_col=None, import_geometry=False):
        import_data = shp2dict(path2shp, import_geometry)
        if import_data is None:
            return self
        add_dict, add_list, wkt = shp2dict(path2shp, import_geometry)
        self.attr_list = unite_lists(self.attr_list, add_list)
        if import_geometry:
            self.wkt = wkt
        self.check()
        if filename_col:
            add_dict = add_constant_col(add_dict, filename_col, path2shp)
        self.add_strings(add_dict)
        return self

    def export_to_shp_points(self, path2shp, attr_exp_dict, x_coord, y_coord, epsg=4326):
        dict2shp_points(path2shp, self.attr, attr_exp_dict, x_coord=x_coord, y_coord=y_coord, epsg=epsg)
        return self

    # Exports all data to shapefile
    # If geometry hasn't been created before it isn't made by this method!
    # ---- still in progress ------
    def export_to_shp(self, path2shp):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.CreateDataSource(path2shp)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(self.epsg)
        lyr = data_source.CreateLayer('Layer', srs, globals()['wkt2ogr'][self.geomtype])
        l = attr_len(attr_dict)
        for key in self.a:
            dtype = col_dict[key]
            field = ogr.FieldDefn(key, dtype)
            if dtype == ogr.OFTString:
                if width is None:
                    width = list_max_len(attr_dict[key])
                field.SetWidth(width)
            lyr.CreateField(field)
        for i in range(l):
            feat = ogr.Feature(lyr.GetLayerDefn())
            for key in col_dict:
                feat.SetField(key, attr_dict[key][0, i])
            if x_coord is not None and y_coord is not None:
                if (x_coord in attr_dict) and (y_coord in attr_dict):
                    x = attr_dict[x_coord][0, i]
                    y = attr_dict[y_coord][0, i]
                    wkt = "POINT(%f %f)" % (np.single(x), np.single(y))
                    point = ogr.CreateGeometryFromWkt(wkt)
                    feat.SetGeometry(point)
            lyr.CreateFeature(feat)
            feat = None
        data_source = None
        return None

    # Import data from csv
    def import_from_csv(self, path2csv, get_col_names=True, delimeter=';', endline=',', filename_col=None):
        csv_dict, csv_list = csv2dict(path2csv, names1st_line=get_col_names, delimeter=delimeter, endline=endline)
        self.attr_list = unite_lists(self.attr_list, csv_list)
        self.check()
        if filename_col:
            add_dict = add_constant_col(csv_dict, filename_col, path2csv)
        self.add_strings(csv_dict)
        return self

    def import_from_xls(self, path2xls, sheet_num=0, get_col_names=True, omit_first_col=False, filename_col=None):
        xls_dict = xls2dict(path2xls, sheet_num=sheet_num, get_col_names=get_col_names, omit_first_col=False)
        self.attr_list = unite_lists(self.attr_list, list(xls_dict.keys()))
        self.check()
        if filename_col:
            add_dict = add_constant_col(xls_dict, filename_col, path2xls)
        self.add_strings(xls_dict)
        return None

    # Export data to xls
    def stats_to_xls(self, path2xls, stats_namelist, length_lim=100000):
        wb = xlwt.Workbook()
        length = min(length_lim, len(self))
        if length < len(self):
            print('Data length exceeds xls limit for %s' % path2xls)
        ws = wb.add_sheet('New_Sheet')
        row = ws.row(0)
        #row.write(export[0][0], 0)
        for col_num in range(len(stats_namelist)):
            row.write(stats_namelist[col_num], col_num + 1)
        for row_num in range(1, length):
            row = ws.row(row_num)
            #row.write(export[0][row_num], 0)
            for col_num in range(len(stats_namelist)):
                row.write(self.attr[col_num][row_num - 1], col_num)
        wb.save(path2xls)
        return None

    # Makes a layer of paired objects by the attribute values
    def pair_by_attributes(self, sep_col, pair_vals, sort_col_list, attr_fin_dict):

        # Define separator column
        try:
            sorter = self[sep_col]
        except:
            raise KeyError('No separator column %s found' % sep_col)

        # Stack columns for searching
        stack_list = []
        for sort_col in sort_col_list:
            if sort_col in self.attr_list:
                stack_list.append(self[sort_col])
        stacked, index = vstack_index(stack_list)

        # Perform pairing
        pair_list = []
        for pair in pair_vals:
            if pair[0] in sorter and pair[1] in sorter:
                mask1 = (sorter == pair[0]).reshape(self.length)
                mask2 = (sorter == pair[1]).reshape(self.length)
                arr1 = stacked.T[mask1]
                arr2 = stacked.T[mask2]
                pair = np.ceil(pair_array(arr1, arr2)).astype(int)
                pair[0] = np.arange(self.length)[mask1][pair[0]]
                pair[1] = np.arange(self.length)[mask2][pair[1]]

                pair_list.append(pair[:2].T[(pair[2]*pair[3]).astype(bool)])
                # Multiple matching in sort columns are considered as a mistake

        # Save paired values indices as an array
        pairing_full = np.vstack(tuple(pair_list)).T

        # Return values of paired columns
        attr2export = [[],[]]
        attr2export_dict = {}
        for attr_col in attr_fin_dict:
            if attr_col in self.attr_list:
                attr_array = self[attr_col]
                for i in [0, 1]:
                    attr_new = '{}_{}'.format(attr_col, i)
                    attr2export[i].append(attr_new)
                    attr2export_dict[attr_new] = attr_array[:, pairing_full[i]]

        attr2export = attr2export[0] + attr2export[1]
        gar2export = geoarray(attr_list=attr2export, attr_dict=attr2export_dict)

        return gar2export

    # Calculates coordinates from degrees, minutes and seconds
    # Second column is not obligatory and float minutes values can be used as well
    def decimal_degrees(self, colname, deg, min, sec=None):
        try:
            dd = decimal_deg(self[deg].astype(np.single), self[min].astype(np.single), self[sec].astype(np.single))
        except:
            print('Failed to calculate coordinates from: %s, %s, %s' % (deg, min, sec))
            return None
        self.attr_list.append(colname)
        self.attr[colname] = dd
        self.width = len(self.attr_list)
        return dd

class geoobject:

    def __init__(self,
                 wkt = False,
                 attr_list=[],
                 attr = {}):

        wkt_for_list = ['POINT', 'LINESTRING', 'POLYGON'] # More complicated wkt types need to be added later
        if wkt:
            assert isinstance(wkt, str)
            for format in wkt_for_list:
                if wkt.startswith(format):
                    self.geotype = format
                else:
                    raise Exception('Unknown geometry type for wkt: %s' % wkt)
                self.wkt = wkt # Maybe another check is needed to confirm validity of wkt data
        self.attr_list, self.attr = attr_check(attr_list, attr)

    def __len__(self):
        return len(self.attr_list)

    def __bool__(self):
        return self.length > 0

    def __getitem__(self, item):
        if key in self.attr:
            return self.attr[item]
        else:
            raise KeyError('No attribute found: %s' % item)

    def set_wkt_point(self, x_col, y_col):
        coord = {'x_col': x_col, 'y_col': y_col}
        for i in ['x_col', 'y_col']:
            if coord[i] not in self.attr_list:
                raise KeyError('No column found: %s' % x_col)
        self.wkt = wkt_point(x_col, y_col)
        return self.wkt

def feat2gobj(feat, import_wkt=False):
    attr_list = feat.keys()
    attr = {}
    for attr_col in attr_list:
        attr[attr_col] = np.array([feat.GetField(attr_col)]).reshape((1,1))
    if import_wkt:
        wkt = feat.geometry().ExportToWkt()
    else:
        wkt = False
    gobj = geoobject(wkt = wkt, attr_list=attr_list, attr=attr)
    return gobj
