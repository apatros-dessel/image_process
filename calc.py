# Contains modules for numpy calculations

import numpy as np

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
def limits_mask(raster_array, lim_list, sign='==', band_mix='AND'):

    # lim_list is a list of limits for each band:
    # for sign = '==': [(0,100,1000), (1,2,3)] means match for all values in band 1 equaled 0, 100 and 1000 and for all bands in band 2 equal to 1,2,3
    # for sign = '<': [0,10] means all values greater than 0 in band 1 and all values greater than 10 in band 2

    if (raster_array.ndim < 2) or (raster_array.ndim > 3):
        print('Error: wrong data: an array of ndim == 3 is needed!')
        return None

    if sign not in ('==', '!=', '>', '<', '>=', '<=', '[]', '()', '[)', '(]', '][', ')(', '](', ')['):
        print('Unreckognized sign: {}'.format(sign))
        return None

    if raster_array.ndim == 2:
        raster_data = [raster_array]
    else:
        raster_data = raster_array

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

        except:
            error_count += 1
            print('Error masking band {}'.format(i+1))

    if error_count >= len(raster_data):
        print('Error creating mask')
        return None

    return mask