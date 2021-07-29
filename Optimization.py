from Protfolio import set_Symbols,set_DataFrames, start, end, symbols
import pandas as pd
import numpy as np
import pandas_datareader.data as web

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



#symbols = ['AAPL', 'RRR', 'FB', 'GOOGL']
set_Symbols(symbols)
stocksList = set_DataFrames(symbols, start, end)
stocks = stocksDF(stocksList, symbols)
log_ret = np.log(stocks / stocks.shift(1))

weights = Read_np_Arr(symbols)

# Expected Return
ep_ret = np.sum((log_ret.mean() * weights) * 252)
print(ep_ret)

# Expected Volatility
exp_vola = np.sqrt(np.dot(weights.T, np.dot(log_ret.cov()*252, weights)))
print(exp_vola)

# Sharp Ratio
SR = ep_ret / exp_vola
print(SR)



