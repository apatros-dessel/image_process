# coding: utf-8

# Package imports
import numpy as np
#import sklearn
#import sklearn.datasets
#import sklearn.linear_model
#from planar_utils import plot_decision_boundary, sigmoid, load_planar_dataset, load_extra_datasets

def do(function, data):
    if function is None:
        return data
    else:
        try:
            return function(data)
        except:
            print('Cannot do: {function}({data})'.format(function, data))
            return data

def relu(x):
    return np.maximum(x, 0)

def layer_sizes(X, Y, n=2):

    n_x = X.shape[0]    # size of input layer
    n_h = n             # size of hidden layer
    n_y = Y.shape[0]    # size of output layer

    return (n_x, n_h, n_y)

def initialize_parameters(n_x, n_h, n_y):

    W1 = np.random.randn(n_h*n_x).reshape((n_h, n_x))*0.01  # W1 -- weight matrix of shape (n_h, n_x)
    b1 = np.zeros((n_h, 1))                                 # b1 -- bias vector of shape (n_h, 1)
    W2 = np.random.randn(n_y*n_h).reshape((n_y, n_h))*0.01  # W2 -- weight matrix of shape (n_y, n_h)
    b2 = np.zeros((n_y, 1))                                 # b2 -- bias vector of shape (n_y, 1)

    parameters = {"W1": W1,
                  "b1": b1,
                  "W2": W2,
                  "b2": b2}

    return parameters

def forward_propagation(X, parameters, functions=[None, None]):

    Z1 = np.dot(parameters['W1'], X) + parameters['b1']
    A1 = do(functions[0], Z1)
    Z2 = np.dot(parameters['W2'], A1) + parameters['b2']
    A2 = do(functions[1], Z2)

    assert(A2.shape == (1, X.shape[1]))

    cache = {"Z1": Z1,
             "A1": A1,
             "Z2": Z2,
             "A2": A2}

    return A2, cache

def compute_cost(A2, Y):

    m = Y.shape[1] # number of example
    # cost = np.sum(Y*np.log(A2)+(1-Y)*np.log((1-A2)))/(-m)
    cost = np.sum(A2 - Y)/m
    cost = float(np.squeeze(cost))  # makes sure cost is the dimension we expect.
                                    # E.g., turns [[17]] into 17
    assert(isinstance(cost, float))

    return cost

def backward_propagation(parameters, cache, X, Y):

    m = X.shape[1]
    W1 = parameters['W1']
    W2 = parameters['W2']
    A1 = cache['A1']
    A2 = cache['A2']

    dZ2 = A2 - Y
    dW2 = np.dot(dZ2, A1.T) / m
    db2 = np.sum(dZ2, axis = 1, keepdims = True) / m
    #dZ1 = np.dot(W2.T, dZ2) * (1 - np.power(A1, 2))
    dZ1 = np.dot(W2.T, dZ2) * (A1>0).astype(int)
    dW1 = np.dot(dZ1, X.T) / m
    db1 = np.sum(dZ1, axis = 1, keepdims = True) / m

    grads = {"dW1": dW1,
             "db1": db1,
             "dW2": dW2,
             "db2": db2}

    #for key in grads.keys():
        #print('{}: {}'.format(key, grads[key]))

    return grads

def update_parameters(parameters, grads, learning_rate = 1.2):

    W1 = parameters['W1']
    b1 = parameters['b1']
    W2 = parameters['W2']
    b2 = parameters['b2']

    W1 = W1 - grads['dW1'] * learning_rate
    b1 = b1 - grads['db1'] * learning_rate
    W2 = W2 - grads['dW2'] * learning_rate
    b2 = b2 - grads['db2'] * learning_rate

    parameters = {"W1": W1,
                  "b1": b1,
                  "W2": W2,
                  "b2": b2}

    return parameters

def nn_model(X, Y, n_h, num_iterations = 10000, print_cost=0):

    n_x = layer_sizes(X, Y)[0]
    n_y = layer_sizes(X, Y)[2]
    parameters = initialize_parameters(n_x, n_h, n_y)

    for i in range(0, num_iterations):
        A2, cache = forward_propagation(X, parameters, functions=[np.tanh, relu])
        cost = compute_cost(A2, Y)
        grads = backward_propagation(parameters, cache, X, Y)
        parameters = update_parameters(parameters, grads)

        if print_cost:
            if i % print_cost == 0:
                print('\nIteration number %i' % i)
                print(A2)
                print("Cost = %f" % cost)
                print('Grads: {}'.format(grads))
                print('Parameters: {}'.format(parameters))

    return parameters

def predict(parameters, X):

    A2, cache = forward_propagation(X, parameters)
    predictions = np.round(A2)

    return predictions

# Build a model with a n_h-dimensional hidden layer
#parameters = nn_model(X, Y, n_h = 4, num_iterations = 10000, print_cost=True)
#predictions = predict(parameters, X)
