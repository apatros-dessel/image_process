import numpy as np

def fill_by_mask(dem_array, mask_array):
    # In mask_array filled pixels're one, empty ones're zero
    assert dem_array.ndim == 2, mask_array.ndim == 2
    assert dem_array.shape == mask_array.shape
    shp = mask_array.shape
    limits = ([None, -1, None, None, 1, None, None, None],
              [1, None, None, None, None, -1, None, None],
              [None, None, 1, None, None, None, None, -1],
              [None, None, None, -1, None, None, 1, None])
    iter = 0
    while True:
        grow = 0
        mask_new = np.copy(mask_array)
        for l in limits:
            mask_change = np.zeros(shp, dtype=np.bool)
            mask_change[l[0]:l[1], l[2]:l[3]][
                mask_array[l[0]:l[1], l[2]:l[3]] < mask_array[l[4]:l[5], l[6]:l[7]]] = True
            mask_change[l[0]:l[1], l[2]:l[3]][dem_array[l[0]:l[1], l[2]:l[3]] > dem_array[l[4]:l[5], l[6]:l[7]]] = False
            grow += len(mask_array[mask_change])
            mask_new[mask_change] = True
        if grow > 0:
            mask_array = mask_new
            iter += 1
        else:
            print('Finished for {} iterations'.format(iter))
            return mask_new

def erosion(arr, iter_num=1):
    # arr must be a 2-dimensional boolean array where True means pixel is whithin area of interest and False if it isn't
    assert arr.ndim == 2
    shp = arr.shape
    # 1. Find neighbour pixels
    limits = ([None, -1, None, None, 1, None, None, None],
              [1, None, None, None, None, -1, None, None],
              [None, None, 1, None, None, None, None, -1],
              [None, None, None, -1, None, None, 1, None])
    while iter<iter_num:
        grow = 0
        mask_new = np.copy(arr)
        for l in limits:
            mask_change = np.zeros(shp, dtype=np.bool)
            arr[l[0]:l[1],l[2]:l[3]][arr[l[0]:l[1],l[2]:l[3]] > arr[l[4]:l[5],l[6]:l[7]]] = True
            grow += len(arr[mask_change])
            mask_new[mask_change] = True
        if grow > 0:
            arr = mask_new
            iter += 1
        else:
            iter = iter_num
    print('Finished for {} iterations'.format(iter))
    return mask_new

def shift(arr1, arr2, iter_num=10000):
    assert arr1.ndim == 2
    assert arr2.ndim == 2
    assert arr1.shape==arr2.shape
    limits = ([None, -1, None, None, 1, None, None, None], # right
              [1, None, None, None, None, -1, None, None], # left
              [None, None, 1, None, None, None, None, -1], # up
              [None, None, None, -1, None, None, 1, None]) # down
    arr2 = np.copy(arr2) # to avoid rewriting the changing array
    iter = 0
    sqe = np.sqrt(np.sum(np.power((arr1-arr2),2))/(arr1.size-1))
    while iter<iter_num:
        n = 0
        sqe_list = [0,0,0,0]
        direct = ['up', 'down', 'right', 'left']
        for l in limits:
            arr1_ = arr1[l[0]:l[1],l[2]:l[3]]
            arr2_ = arr2[l[4]:l[5],l[6]:l[7]]
            sqe_list[n] = np.sqrt(np.sum(np.power((arr1_-arr2_),2))/(arr1.size-1))
            n += 1
        sqe_new = min(sqe_list)
        if sqe_new < sqe:
            n = sqe_list.index(sqe_new)
            arr2 = move_array(arr2, n)
            sqe = sqe_new
            print("Moved {} at {} iteration with SQE={}".format(direct[n], iter+1, sqe))
            iter += 1
        else:
            print('Finished for {} iterations'.format(iter))
            iter = iter_num
    #print('Finished for {} iterations'.format(iter))
    return arr2

# Moves an array from the predefined boreder adding a new line calculated from its neighbours
def move_array(np_array, n=0, axis=None, forward=None):
    assert np_array.ndim==2
    n_vals = [[0,0],[0,1],[1,1],[1,0]]
    if axis is None:
        axis = bool(n_vals[n][0])
    else:
        axis = bool(axis)
    if forward is None:
        forward = bool(n_vals[n][1])
    else:
        forward = bool(forward)
    if axis:
        np_array = np_array.T
    if forward:
        source = np.concatenate((np_array[2], np_array[1], np_array[0])).reshape((3, np_array.shape[1])).T
        order_tuple = (np.dot(source, np.array([[1],[-3],[3]])).T, np_array[:-1])
    else:
        source = np_array[-3:].T
        order_tuple = (np_array[1:], np.dot(source, np.array([[1], [-3], [3]])).T)
    np_array = np.concatenate(order_tuple)
    if axis:
        np_array = np_array.T
    return np_array

