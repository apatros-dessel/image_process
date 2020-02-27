# -*- coding: utf-8 -*-

# Contains modules for numpy calculations

import numpy as np
from raster_data import RasterData
from tools import obj2list

# Define limits of array values
def arrlim(arr, value):
    assert (value >= 0 and value <= 1)
    item = int(arr.size * value - 1)
    if item < 0:
        item = 0
    return arr[arr.argsort()[item]]

def make_class_table(min = None, max = None, values = None):
    nomin = (min is None)
    nomax = (max is None)
    if values is not None:
        values = [0, 1]
    if nomin and nomax:
        return [[None, 0, values[0]], [0, None, values[1]]]
    elif (not nomin) and (not nomax):
        assert len(min) == len(max)
    if nomin:
        max = min + [None]
    elif nomax:
        min = [None] + max
    assert len(min) == len(values)
    class_table = []
    for i in range(len(min)):
        class_table.append([min[i], max[i], values[i]])
    return class_table

# Checks raster arrays' number of dimensions and returns a list with a single array if it equals 2
def array3dim(raster_array):
    if raster_array.ndim == 2:
        raster_array = np.array([raster_array])
    elif raster_array.ndim != 3:
        raise Exception('Incorrect band_array shape: {}'.format(raster_array.shape))
    return raster_array

# Makes classification of an array
def segmentator(band_array, borders = [[None, 0, 0], [0, None, 1]]):
    class_array = np.copy(band_array)
    min_range = 0
    max_range = len(borders)
    if (borders[0][0] is None) and (borders[0][1] is not None):
        class_array[class_array < borders[0][1]] = borders[0][2]
        min_range = 1
    if (borders[-1][1] is None) and (borders[-1][0] is not None):
        class_array[class_array >= borders[-1][0]] = borders[-1][2]
        max_range -= 1
    for i in range(min_range, max_range):
        class_array[(class_array > borders[i][0]) * (class_array <= borders[i][1])] = borders[i][2]
    return class_array

# Makes a mask from raster array
def limits_mask(raster_array, lim_list, sign='==', band_mix='AND', include_ = None, exclude_ = None, include_raster_nodata=0):

    # lim_list is a list of limits for each band:
    # for sign = '==': [(0,100,1000), (1,2,3)] means match for all values in band 1 equaled 0, 100 and 1000 and for all bands in band 2 equal to 1,2,3
    # for sign = '<': [0,10] means all values greater than 0 in band 1 and all values greater than 10 in band 2

    if isinstance(raster_array, RasterData):
        if (raster_array.data != 2):
            raster_array = raster_array.getting(2)
        raster_data = raster_array

    else:

        raster_nodata = 0

        if (raster_array.ndim < 2) or (raster_array.ndim > 3):
            print('Error: wrong data: an array of ndim == 3 is needed!')
            return None

        if raster_array.ndim == 2:
            raster_data = [raster_array]
        else:
            raster_data = raster_array

    if sign not in ('==', '!=', '>', '<', '>=', '<=', '[]', '()', '[)', '(]', '][', ')(', '](', ')['):
        print('Unreckognized sign: {}'.format(sign))
        return None

    if band_mix == 'AND':
        mask = np.ones(raster_data[0].shape).astype(np.bool)
    elif band_mix == 'OR':
        mask = np.zeros(raster_data[0].shape).astype(np.bool)
    else:
        print('Unknown band_mix - {}, "AND" or "OR" is needed'.format(band_mix))
        return None

    error_count = 0

    for i, limits in enumerate(lim_list):

        if i > len(raster_data):
            continue

        if limits is None:
            continue

        try:

            new_mask = np.zeros(raster_data[0].shape).astype(np.bool)

            if sign in ('==', '!=', '[]', '()', '[)', '(]', '][', ')(', '](', ')['):

                if not isinstance(limits, tuple):
                    print('Wrong limit type for band {}: {}; a tuple is needed, unable to make a mask'.format(i+1, type(limits)))
                    continue

                if sign in ('[]', '()', '[)', '(]', '][', ')(', '](', ')['):
                    if len(limits) > 2:
                        print('Warning: only first two values will be used for min/max limits')
                    for band in raster_data:
                        if sign=='[]':
                            new_mask[(band >= limits[0]) * (band <= limits[1])]
                        elif sign=='()':
                            new_mask[(band > limits[0]) * (band < limits[1])]
                        elif sign=='[)':
                            new_mask[(band >= limits[0]) * (band < limits[1])]
                        elif sign=='(]':
                            new_mask[(band > limits[0]) * (band <= limits[1])]
                        elif sign=='][':
                            new_mask[(band <= limits[0]) + (band >= limits[1])]
                        elif sign==')(':
                            new_mask[(band < limits[0]) + (band > limits[1])]
                        elif sign=='](':
                            new_mask[(band <= limits[0]) + (band > limits[1])]
                        elif sign==')[':
                            new_mask[(band < limits[0]) + (band >= limits[1])]

                else:
                    for band in raster_data:
                        for value in limits:
                            if sign == '==':
                                new_mask[band==value] = True
                            elif sign == '!=':
                                new_mask[band!=value] = True

            elif sign in ('>', '<', '>=', '<='):
                if isinstance(limits, (tuple, list)):
                    print('Wrong limit type for band {}: {}; only first two values will be used for more/less limits'.format(i+1, type(limits)))
                    limits = limits[0]
                for band in raster_data:
                    if sign == '>':
                        new_mask[band>limits] = True
                    elif sign == '<':
                        new_mask[band<limits] = True
                    elif sign == '>=':
                        new_mask[band>=limits] = True
                    elif sign == '<=':
                        new_mask[band<=limits] = True

            if band_mix == 'AND':
                mask = mask * new_mask
            elif band_mix == 'OR':
                mask = mask + new_mask

            del new_mask

            if include_ is not None:
                mask[band == include_] = True

            if exclude_ is not None:
                mask[band == exclude_] = False

            if raster_nodata:
                nodata = raster_data.ds.GetRasterBand(raster_data.bannums[i]).GetNoDataValue()
                if raster_nodata == 1:
                    mask[band == nodata] = True
                elif raster_nodata == -1:
                    mask[band == nodata] = False

            del band

        except:
            error_count += 1
            print('Error masking band {}'.format(i+1))

    if error_count >= len(raster_data):
        print('Error creating mask')
        return None

    return mask

def get_raster_limits(raster_array, method=0, band_limits = None):

    method_list = [
        'Min/Max',  # Minimum/maximum values of the array
        'Mean+-SD',  # Mean-Sd/Mean+SD
        'Count_Cut',  # Percent of all values in the array
        "Custom",  # User-defined values of min/max
    ]

    # print(method_list[method])

    band_limits_defaults = [
        None,
        (2, 2),
        (0.02, 0.98),
        (1, 255),
    ]

    if band_limits is None:
        method = 0

    if (method == method_list[0]) or (method == 0):                # Min/Max
        min = np.min(raster_array)
        max = np.max(raster_array)

    elif (method == method_list[1]) or (method == 1):              # Mean+-SD
        mean = np.mean(raster_array)
        sd = np.std(raster_array)
        min = mean - (band_limits[0] * sd)
        max = mean + (band_limits[1] * sd)

    elif (method == method_list[2]) or (method == 2):              # Count_Cut
        min = arrlim(raster_array, band_limits[0])
        max = arrlim(raster_array, band_limits[1])


    elif (method == method_list[3]) or (method == 3):            # Custom
        min = band_limits[0]
        max = band_limits[1]

    else:
        print('Unknown hystogram limits')
        return None, None

    # print(min, max)

    return  min, max

def data_to_image(raster_array, method=0, band_limits=None, gamma=1):

    min, max = get_raster_limits(raster_array, method=method, band_limits = band_limits)

    # print('min = {}, max = {}'.format(min, max))

    y_min = 1
    y_max = 255
    dy = 254

    dx = (max - min)
    raster_array = raster_array.astype(np.float)
    raster_array = raster_array - min

    raster_array[raster_array < 0] = 0
    raster_array[raster_array > dx] = dx

    # print(np.unique(raster_array))

    if gamma == 1:
        raster_array = (raster_array * (float(dy) / float(dx))).astype(np.int)
    else:
        raster_array = raster_array / float(dx)
        raster_array = raster_array ** gamma
        raster_array = (raster_array * float(dy)).astype(np.int)

    # print(np.unique(raster_array))

    raster_array = raster_array + y_min
    raster_array[raster_array < y_min] = y_min
    raster_array[raster_array > y_max] = y_max
    raster_array = np.asarray(raster_array)

    # print(np.unique(raster_array))

    return raster_array

def NDVI(red, nir):
    ndvi = ((nir - red) / (nir + red))
    return NDVI

# Adjusted ndvi for better forest border detection
def NDVI_adj(red, nir):
    ndvi_adj = ((nir - red) / (nir + red)) / (nir * red)
    return ndvi_adj

def SAVI(red, nir, L):
    savi = ((nir - red) / (nir + red - L)) * (L + 1)
    return savi

def SAVI1(red, nir):
    dnir = nir * 2 + 1
    L = (dnir - np.sqrt((dnir ** 2 - (nir * red) * 8))) / 2
    savi = SAVI(red, nir, L)
    return savi

def SAVI2(red, nir):
    savi = SAVI1(red, nir)
    return savi

# Makes changes mask for a set of arrays
# !!! All arrays in the array_set must have the same shape
def band_by_limits(array_set, upper_lims = None, lower_lims = None, check_all_values = False, upper_priority = True):

    mask = np.zeros(array_set[0].shape).astype(int)

    if lower_lims is not None:
        lower_lims = obj2list(lower_lims)
        lower_lims = list(lower_lims)
        lower_lims.sort()
        lower_mask = np.zeros(array_set[0].shape).astype(int)
        for arr in array_set:
            for i, val in enumerate(lower_lims):
                lower_mask[arr<val] = -(len(lower_mask)-i)
                if check_all_values:
                    lower_mask[arr<val] = 0

    if upper_lims is not None:
        upper_lims = obj2list(upper_lims)
        upper_lims = list(upper_lims)
        upper_lims.sort(reverse=True)
        upper_mask = np.zeros(array_set[0].shape).astype(int)
        for arr in array_set:
            for i, val in enumerate(upper_lims):
                upper_mask[arr < val] = len(upper_lims) - i
                if check_all_values:
                    upper_mask[arr < val] = 0

    if (upper_lims is not None):

        if (lower_lims is not None):

            if upper_priority:
                upper_lims[upper_lims==0] = lower_lims[upper_lims==0]
                return upper_lims

            else:
                lower_lims[lower_lims == 0] = upper_lims[lower_lims == 0]
                return lower_lims

        else:
            return upper_lims

    elif (lower_lims is not None):
        return lower_lims

# Makes mask of band by values
def band_mask(arr, min_val = None, max_val = None, include_min = False, include_max = False):

    mask = np.zeros(arr.shape).astype(bool)

    if min_val is not None:
        if max_val is not None:
            if min_val == max_val:
                mask = (arr == min_val)
            else:
                mask = (arr > min_val) * (arr < max_val)
        else:
            mask = (arr > min_val)
    elif max_val is not None:
        mask = (arr < max_val)
    else:
        print('No limit values found, unable to make mask')
        mask = None

    if mask is not None:
        if include_min:
            mask[arr == min_val] = True
        if include_max:
            mask[arr == max_val] = True

    return mask

''' RASTER FILTERS '''

# Deletes all neighbors in path (4-heighbor rule)
def erode(source_array, iter_num = 1):
    # In mask_array filled pixels're one, empty ones're zero
    mask_array = np.copy(source_array).astype(int)
    limits = ([None, -1, None, None, 1, None, None, None],
              [1, None, None, None, None, -1, None, None],
              [None, None, 1, None, None, None, None, -1],
              [None, None, None, -1, None, None, 1, None])
    iter = 0
    while iter < iter_num:
        degrow = 0
        mask_new = np.copy(mask_array)
        for l in limits:
            mask_change = np.zeros(mask_array.shape, dtype=np.bool)
            mask_change[l[0]:l[1], l[2]:l[3]][
                mask_array[l[0]:l[1], l[2]:l[3]] > mask_array[l[4]:l[5], l[6]:l[7]]] = True
            degrow += len(mask_array[mask_change])
            mask_new[mask_change] = False
        if degrow > 0:
            mask_array = mask_new
            iter += 1
        else:
            print('Finished for {} iterations'.format(iter))
            iter = iter_num
    return mask_new

# Deletes all neighbors in path (4-heighbor rule)
def engrow(source_array, iter_num = 1):
    # In mask_array filled pixels're one, empty ones're zero
    mask_array = np.copy(source_array).astype(int)
    limits = ([None, -1, None, None, 1, None, None, None],
              [1, None, None, None, None, -1, None, None],
              [None, None, 1, None, None, None, None, -1],
              [None, None, None, -1, None, None, 1, None])
    iter = 0
    while iter < iter_num:
        degrow = 0
        mask_new = np.copy(mask_array)
        for l in limits:
            mask_change = np.zeros(mask_array.shape, dtype=np.bool)
            mask_change[l[0]:l[1], l[2]:l[3]][
                mask_array[l[0]:l[1], l[2]:l[3]] > mask_array[l[4]:l[5], l[6]:l[7]]] = True
            degrow += len(mask_array[mask_change])
            mask_new[mask_change] = False
        if degrow > 0:
            mask_array = mask_new
            iter += 1
        else:
            print('Finished for {} iterations'.format(iter))
            iter = iter_num
    return mask_new

def splitbin(arr1, arr2):
    if arr1.shape != arr2.shape:
        print('Array shapes doesnt match')
    arr_sum = np.zeros(arr1.shape)
    for i in range(arr1.size):
        arr_sum[i] = np.sum(arr1[:i]) + np.sum(arr2[i:])
    return np.argsort(arr_sum)[0]