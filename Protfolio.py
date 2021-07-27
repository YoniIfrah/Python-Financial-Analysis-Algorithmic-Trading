import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt




def set_Symbols():
    print("Enter 4 symbols")
    i = 0
    while i < 4:
        symbol = input("Enter symbol number {}:".format(i+1)).upper()
        if symbol in symbols:
            print("cannot enter the same stock twice please try again...")
            i -= 1
        else:
            symbols.append(symbol)
        i += 1

def set_DataFrames(symbols):
    # Dates
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2021, 1, 1)

    stockList = []
    errCheck = 0
    try:
        for item in symbols:
            stockList.append(web.DataReader(item, 'yahoo', start, end))
            errCheck += 1

    except:
        errMessage = str(symbols[errCheck]) + " symbol is invalid"
        raise Exception(errMessage)

    return stockList


def Add_Normed_Return(stocks):
    for stock_df in stocks:
        stock_df['Normed Return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']

def Add_Allocation(stocks):
    # 25% in stockList[0]
    # 25% in stockList[1]
    # 25% in stockList[2]
    # 25% in stockList[3]
    for stock_df, allo in zip(stocks,[.25,.25,.25,.25]):
        stock_df['Allocation'] = stock_df['Normed Return'] * allo

def Add_Position_Values(stocks):
    invest = float(input("How much money do you invest?\n"))
    for stock_df in stocks:
        stock_df['Position Values'] = stock_df['Allocation'] * invest
    return invest

def set_All_Pos_Vals(stocks):
    all_pos_vals = [item['Position Values'] for item in stocks]
    protfolio_val = pd.concat(all_pos_vals, axis=1)
    protfolio_val.columns = [item+' Pos Val' for item in symbols]
    protfolio_val['Total Pos'] = protfolio_val.sum(axis=1)
    return protfolio_val

def Total_Pos_Plot(protfolio_val):
    protfolio_val['Total Pos'].plot(figsize=(12, 8))
    plt.title('Total Portfolio Value')
    plt.show()

def Stocks_Pos_plot(protfolio_val):
    protfolio_val.drop('Total Pos', axis=1).plot(figsize=(12, 8))
    plt.title('Total Portfolio Value')
    plt.show()




symbols = []
set_Symbols()

stockList = set_DataFrames(symbols)
Add_Normed_Return(stockList)
Add_Allocation(stockList)
invest = Add_Position_Values(stockList)

protfolio_val = set_All_Pos_Vals(stockList)
Total_Pos_Plot(protfolio_val)
Stocks_Pos_plot(protfolio_val)

