from Protfolio import set_Symbols,set_DataFrames, start, end, symbols
import pandas as pd
import numpy as np
from scipy.optimize import minimize

import matplotlib.pyplot as plt

def stocksDF(stockList, symbols):

    stocks = pd.concat([stockList[0]['Close'], stockList[1]['Close'], stockList[2]['Close'], stockList[3]['Close']], axis=1)
    stocks.columns = [symbols[0], symbols[1], symbols[2], symbols[3]]

    return stocks

def Read_np_Arr(symbols):
    """
    Here we will define amount of percent for each share we want to invest by using array of float numbers
    note that the sum of the array MUST be equal to 1 so it will be 100%
    :return: object, numpy array
    """
    n = len(symbols)
    counter = 1
    i = 0
    arr = np.zeros(n, dtype=float) # Reset array to zeros
    print("Enter the percentages amounts (note that the sum need to be equal to 1):")
    while i < n:
        arr[i] = float(input("percentages amount for {}: ".format(symbols[i])))

        # Autofill after 5 tries
        if counter == 5:
            print("after 5 tries sets all to be 0.25")
            for j in range(n):
                arr[j] = 0.25
            break
        # Check if the amount is equal to
        if np.sum(arr) > 1:
            print("Error sum is not equal to 1 please try again...")
            arr = np.zeros(n, dtype=float)
            i = -1
            counter += 1

        i += 1
    return arr

def Reset_Simulation(num_ports):
    all_weights = np.zeros((num_ports, len(stocks.columns)))
    ret_arr = np.zeros(num_ports)
    vola_arr = np.zeros(num_ports)
    sharpe_arr = np.zeros(num_ports)

    return all_weights, ret_arr, vola_arr, sharpe_arr

def Random_Weights(symbols):
    weights = np.array((np.random.random(4)))
    weights = weights / np.sum(weights)

    return weights

def Simulations(num_ports):

    for index in range(num_ports):
        # Weights
        weights = Random_Weights(symbols)

        # Save the weights
        all_weights[index, :] = weights

        # Expected Return
        ret_arr[index] = np.sum((log_ret.mean() * weights) * 252)

        # Expected Volatility
        vola_arr[index] = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))

        # Sharp Ratio
        sharpe_arr[index] = ret_arr[index] / vola_arr[index]


def Plot_Display(ret_arr, vola_arr, sharpe_arr):
    """
    Here we will get the display of the sharpe ratio "bullet" as more we get bullet curve the better
    stocks combination we have
    :param ret_arr: Object, numpy array of return values
    :param vola_arr: Object, numpy array of volatility values
    :param sharpe_arr: Object, numpy array of the sharpe ratios
    :return: None
    """
    max_sr_ret = ret_arr[sharpe_arr.argmax()]
    max_sr_vola = vola_arr[sharpe_arr.argmax()]
    plt.figure(figsize=(10,6))
    plt.scatter(vola_arr, ret_arr, c=sharpe_arr, cmap='plasma')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel("Volatility")
    plt.ylabel("Return")
    plt.scatter(max_sr_vola, max_sr_ret, c='red', s=50, edgecolors='black')

    # adding grid to the graph
    plt.grid()
    plt.show()


def get_ret_vola_sr(weights):
    weights = np.array(weights)
    ret = np.sum(log_ret.mean() * weights) * 252
    vola = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))
    sr = ret / vola

    return np.array([ret, vola, sr])

def neg_sharpe(weights):
    return (get_ret_vola_sr(weights)[2] * (-1))

def check_sum(weights):
    # Return 0 if the sum of the weights is 1
    return np.sum(weights) - 1


def Frontier(init_guess, bounds):
    max_sr_ret = ret_arr[sharpe_arr.argmax()]
    max_sr_vola = vola_arr[sharpe_arr.argmax()]

    frontier_y = np.linspace(max_sr_vola-0.05, max_sr_ret+0.15, 25)

    def minimize_volatility(weights):
        return get_ret_vola_sr(weights)[1]

    frontier_volatility = []
    for possible_return in frontier_y:
        cons = ({'type': 'eq', 'fun': check_sum},
                {'type': 'eq', 'fun': lambda w: get_ret_vola_sr(w)[0]-possible_return})
        result = minimize(minimize_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
        frontier_volatility.append(result['fun'])

    return frontier_volatility, frontier_y


def Plot_Frontier(frontier_volatility, frontier_y):

    plt.figure(figsize=(10, 6))
    plt.scatter(vola_arr, ret_arr, c=sharpe_arr, cmap='plasma')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel("Volatility")
    plt.ylabel("Return")

    # Red Dot
    plt.scatter(vola_arr[sharpe_arr.argmax()], ret_arr[sharpe_arr.argmax()], c='red', s=50, edgecolors='black')

    # Linespace
    plt.plot(frontier_volatility, frontier_y, 'g--', linewidth=3)

    # Grid
    plt.grid()

    plt.show()

def set_Opt_Result():
    cons = ({'type': 'eq', 'fun': check_sum})
    bounds = ((0, 1), (0, 1), (0, 1), (0, 1))
    init_guess = [0.25, 0.25, 0.25, 0.25]
    opt_results = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
    return opt_results, init_guess, bounds



set_Symbols(symbols)
stocksList = set_DataFrames(symbols)
stocks = stocksDF(stocksList, symbols)
log_ret = np.log(stocks / stocks.shift(1))




# Number of tries to find the best allocation
num_ports = 5000
#np.random.seed(101)

all_weights, ret_arr, vola_arr, sharpe_arr = Reset_Simulation(num_ports)


def drive():
    Simulations(num_ports)

    print("share ratio max: ", sharpe_arr.max())

    print("share ratio argmax: ", sharpe_arr.argmax())

    opt_results, init_guess, bounds = set_Opt_Result()

    print("get_ret_vola_sr(opt_results.x): ", get_ret_vola_sr(opt_results.x))

    frontier_volatility, frontier_y = Frontier(init_guess, bounds)

    Plot_Frontier(frontier_volatility, frontier_y)

    #Getting the best allocation out of the all the simulations
    print("all_weights[sharpe_arr.argmax(), :]: ", all_weights[sharpe_arr.argmax(), :])


drive()
