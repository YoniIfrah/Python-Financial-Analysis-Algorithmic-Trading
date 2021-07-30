from Protfolio import set_Symbols,set_DataFrames, start, end, symbols
import pandas as pd
import numpy as np

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
    plt.show()



# Default stocks combination
#symbols = ['AAPL', 'TSLA', 'FB', 'MSFT']

set_Symbols(symbols)
stocksList = set_DataFrames(symbols, start, end)
stocks = stocksDF(stocksList, symbols)
log_ret = np.log(stocks / stocks.shift(1))

# Number of tries to find the best allocation
num_ports = 5000
#np.random.seed(101)

all_weights, ret_arr, vola_arr, sharpe_arr = Reset_Simulation(num_ports)


def drive():
    Simulations(num_ports)

    print("share ratio max: ", sharpe_arr.max())

    print("share ratio argmax: ",sharpe_arr.argmax())

    #Getting the best allocation out of the all the simulations
    print(all_weights[sharpe_arr.argmax(), :])

    Plot_Display(ret_arr, vola_arr, sharpe_arr)

drive()
