# Makes forest height correction to slope aspect and steepness

import os
import gdal
import numpy as np
from copy import deepcopy
import csv
import sing_layer

def adapt2slope(dH, slope, aspect, dem, c=np.zeros(6).astype(float), order0=1, order_fin=5, iternum=1000, print_coefs=False):

    order = order0

    while order <= order_fin:

        grad = 0.1 ** order
        iter = 1

        while iter <= iternum:

            slope_eff = slope_effect(dH, slope, aspect, dem, c)
            change = False

            if print_coefs:
                #print('Coefs for iter %i: ' % iter, c)
                print('Slope: ', slope_eff)

            for i in range(len(c)):
                c_min = deepcopy(c)
                c_min[i] = c_min[i] - grad
                c_max = deepcopy(c)
                c_max[i] = c_max[i] + grad
                s_e_min = slope_effect(dH, slope, aspect, dem, c_min)
                s_e_max = slope_effect(dH, slope, aspect, dem, c_max)
                if s_e_min <= s_e_max:
                    if s_e_min < slope_eff:
                        c[i] = c_min[i]
                        change = True
                elif s_e_max < slope_eff:
                    c[i] = c_max[i]
                    change = True
                print('k_%i = %f' % (i, c[i]))

            if not change:
                print('Finished order %i for %i iterations' % (order, iter))
                iter = iternum + 1
            else:
                iter += 1

        #print('Finished order %i for %i iterations' % (order, iter))

        order += 1

    #print('Finished')

    return c

def adapt2slope_derivative(dH, slope, aspect, k_1=0, k_2=0, k_3=0, grad=0.01, learn_rate=0.01, iternum=1000, print_coefs=False):
    c = [k_1, k_2, k_3]
    for iter in range(iternum):
        slope_eff = abs(slope_effect(dH, slope, aspect, c))
        for i in range(3):
            c_max = deepcopy(c)
            c_max[i] = c_max[i] + grad
            s_e_max = abs(slope_effect(dH, slope, aspect, c_max))
            c[i] = c[i] - learn_rate * (s_e_max - slope_eff)
            if print_coefs:
                print('k_%i = %f' % (i+1, c[i]))
        if print_coefs:
            print('Slope[%i] = %f ' % (iter+1, slope_eff))
    return c

def slope_effect(dH, slope, aspect, dem, c=np.zeros(6).astype(float)):
    dHnew = recalc_dh(dH, slope, aspect, dem, c)
    slope_eff = np.std(dHnew - dH)
    return float(slope_eff)

def recalc_dh(dH, slope, aspect, dem, c):
    sin_a = np.sin(aspect + c[0])
    tan_s = np.tan(slope + c[1])
    dHnew = c[2]*sin_a + c[3]*tan_s + c[4]*dem + c[5]
    return dHnew

def sim_dh(dH, slope, aspect, dem, c):
    a_c = aspect + c[0]
    s_c = slope + c[1]
    sin_a = np.sin(a_c)
    tan_s = np.tan(s_c)

    dHsim = c[2]*dem + c[3]*np.tan(s_c) + c[4]*np.sin(a_c)
    '''
    dc = np.copy(c)
    dc[0] = np.mean(c[3]*np.cos(a_c))
    dc[1] = np.mean(c[4] / np.cos(s_c) ** 2)
    dc[2] = np.mean(dem)
    dc[3] = np.mean(np.sin(a_c))
    dc[4] = np.mean(np.tan(s_c))

    dc = np.copy(c)
    dc[0] = np.mean((tan_s * np.cos(a_c)) * c[2])
    dc[1] = np.mean((c[2] * sin_a) / (np.cos(s_c) ** 2))
    n = dem * tan_s * sin_a
    dc[2] = np.mean(n)

    dHsim = c[2]* n
    '''

    return dHsim, dc

def adapt2dem(dH, slope, aspect, dem, c=np.zeros(5), learn_rate=0.1, iternum=100, print_cost=False):
    cost_list = []
    for i in range(iternum):
        dHsim, dc = sim_dh(slope, aspect, dem, c)
        c = c - learn_rate * dc
        cost = np.std(dHsim - dH)
        cost_list.append(cost)
        if print_cost:
            print(cost)
    return c, cost_list

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
        if names_list[num] in csvdata:
            col_name = '{}_2'.format(names_list[num])
            copy_num = 2
            while col_name in csvdata:
                copy_num += 1
                col_name = '{}_{}'.format(names_list[num], copy_num)
        else:
            col_name = names_list[num]
        csvdata[col_name] = read_list[:,num].reshape((1,len(read_list)))
    return csvdata, names_list

path = r'C:\sadkov\forest\Sept_test\dem\kluchevskoie\tif'
os.chdir(r'C:\sadkov\forest\Sept_test\dem\kluchevskoie\tif')

def test_tif(path2slope = r'Slope_topo_Kluchevskoie_shifted2srtm.tif',
            path2aspect = r'Aspect_topo_Kluchevskoie_shifted2srtm.tif',
            path2dem = r'dem_topo_Kluchevskoie_shifted2srtm_adapted.tif',
            path2dH = r'dH.tif', path2newH = r'dHnew.tif'):

    slope = np.radians(gdal.Open(path2slope).ReadAsArray())
    aspect = np.radians(gdal.Open(path2aspect).ReadAsArray())
    dem = np.radians(gdal.Open(path2dem).ReadAsArray())
    dH = gdal.Open(path2dH).ReadAsArray()

    c = adapt2slope(dH, slope, aspect, dem, print_coefs=True)
    #c = adapt2slope_derivative(dH, slope, aspect, print_coefs=True)

    x, newH = recalc_dh(dH, slope, aspect, dem, c)
    print(np.unique(dH), np.unique(newH))

    driver = gdal.GetDriverByName('GTiff')
    outData = driver.CreateCopy(path2newH, gdal.Open(path2dH), 1)
    outData.GetRasterBand(1).WriteArray(newH)
    outData = None
    return None

def test_csv(path2csv = r'data_test_small_small.csv'):
    data = csv2dict(path2csv)[0]
    slope = np.radians(data['Slope_topo_Kluchevskoie_shifted2srtm_'].astype(float))
    aspect = np.radians(data['Aspect_topo_Kluchevskoie_shifted2srtm_'].astype(float))
    dem = data['dem_topo_Kluchevskoie_shifted2srtm_adapted_'].astype(float)
    dH = data['dH_srtm_corr_'].astype(float)

    c = adapt2slope(dH, slope, aspect, dem, order_fin = 5, print_coefs=True)
    newH = recalc_dh(dH, slope, aspect, dem, c)
    print(np.unique(dH))
    print(np.unique(newH))

    #adapt2dem(dH, slope, aspect, dem, print_cost=True)

    return None

def neuron_csv(path2csv = r'data_test_small_small.csv', num_iterations=100, learning_rate=0.001, print_cost = False):

    data = csv2dict(path2csv)[0]
    slope = np.radians(data['Slope_topo_Kluchevskoie_shifted2srtm_'].astype(float))
    aspect = np.radians(data['Aspect_topo_Kluchevskoie_shifted2srtm_'].astype(float))
    dem = data['dem_topo_Kluchevskoie_shifted2srtm_adapted_'].astype(float)
    dH = data['dH_srtm_corr_'].astype(float)

    X = np.vstack((dem, slope, aspect))
    Y = dH

    #print(X.shape, Y.shape)

    #parameters = nn_model(X, Y, n_h=4, num_iterations=10, print_cost=True)
    #for key in parameters.keys():
        #print('{}: {}'.format(key, parameters[key]))
    #predictions = predict(parameters, X)
    #print(predictions)

    w, b = sing_layer.initialize_with_zeros(X.shape[0])
    params, grads, costs = sing_layer.optimize(w, b, X, Y, num_iterations, learning_rate, print_cost = print_cost)
    predictions = np.dot(params['w'].T, X) + params['b']

    print(predictions)

    return predictions

#test_csv()
#test_tif()
neuron_csv(num_iterations=1000, print_cost=True)

