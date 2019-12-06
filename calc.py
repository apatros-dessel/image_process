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
        class_array[class_array > borders[i][0] and class_array <= borders[i][1]] = borders[i][2]
    return class_array