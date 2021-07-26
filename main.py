from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DateLocator, MONDAY
import numpy as np

def Add_EWMA(ax, df):
    df["EWMA-12"] = df["Close"].ewm(span=12).mean()
    ax.plot(df['Date'], df['EWMA-12'], ls='-.', label='EWMA 12', alpha=0.5)


def Add_Upper_and_Lower(ax, df):
    # upper = 13MA + 2*std(13)
    ax.plot(df['Date'], df.rolling(window=13).mean()['Close'] + 2 * df['Close'].rolling(13).std(),
            ls='--', label='Upper', alpha=0.3)

    # lower = 13MA - 2*std(13)
    ax.plot(df['Date'], df.rolling(window=13).mean()['Close'] - 2 * df['Close'].rolling(13).std(),
            ls='--', label='Lower', alpha=0.3)

def Add_MA(ax, df, time):
    if time == 'weekly' or time == 'daily':
        # MA of 34 closes
        ax.plot(df['Date'], df.rolling(window=34).mean()['Close'], label='Close 34 MA', alpha=0.7, linewidth=0.5)
        # MA of 55 closes
        ax.plot(df['Date'], df.rolling(window=55).mean()['Close'], label='Close 55 MA', alpha=0.7, linewidth=0.5)

        if time == 'daily':
            # MA of 233 closes
            ax.plot(df['Date'], df.rolling(window=233).mean()['Close'], label='Close 233 MA', alpha=0.7,
                       linewidth=0.5)
        else:
            # MA of 13 closes
            ax.plot(df['Date'], df.rolling(window=13).mean()['Close'], label='Close 13 MA', alpha=0.7, linewidth=0.5)


def VisualizingChart(Excel_File, stock):
    """
    This function will display the chart of the stock by different time frames with matplotlib
    :param Excel_File: string, The path of the excel file
    :param stock: string, Stock name
    :return: None
    """
    print("please wait building charts from excel file...")
    figure, axis = plt.subplots(2, 2, figsize=(12,8)) # figure is object and axis is the 2x2 graphs matrix
    k = 0
    arr = ['monthly', 'weekly', 'daily', 'daily']  # list of the time frames

    for i in axis:
        for chart in i:
            # take each time different dataframe from the excel file
            df = pd.read_excel(Excel_File, sheet_name=arr[k])
            # if you want to add another lines to the chart add another line of code like this
            chart.plot(df['Date'], df['Close'], linewidth=1, label='Close')

            # Adding indicators
            Add_Upper_and_Lower(chart, df)
            Add_MA(chart, df, arr[k])
            Add_EWMA(chart, df)


            #adding grid to the graph
            chart.xaxis.grid(True)
            chart.yaxis.grid(True)

            #setting labels of the graphs
            chart.set_xlabel("Dates")
            chart.set_ylabel("$ Price")
            chart.set_title(stock + " " + arr[k])
            chart.legend(loc=0) # add the label string inside the chart
            k += 1

    print("Done !")
    plt.tight_layout()
    plt.show()


def WriteToExcel(df_daily, df_weekly, df_monthly, stock):
    """
    here we will choose where to save our Excel file on the computer then
    we are creating excel file of the daily, weekly and monthly stock time frames in one excel when
    each time frame has a page of his own
    :return:saved excel named by the stock
    """

    filePath = filedialog.askdirectory()+"\\"#choosing where to locate the excel file with GUI

    if filePath == "\\": #if the user press cancel for selecting file location
        print("The file will be saved where is the python file")
        filePath = ""

    ExcelName = filePath+stock+".xlsx"
    print("trying to write to excel file...")
    try:
        #in order to make a few sheets we must use ExcelWriter
        writer = pd.ExcelWriter(ExcelName, engine='xlsxwriter')

        # Adding stock history

        df_monthly.to_excel(writer, sheet_name='monthly')

        df_weekly.to_excel(writer, sheet_name='weekly')

        df_daily.to_excel(writer, sheet_name='daily')

        # Adding stock description

        df_daily.describe().to_excel(writer, sheet_name='describe daily')

        df_weekly.describe().to_excel(writer, sheet_name='describe weekly')

        df_monthly.describe().to_excel(writer, sheet_name='describe monthly')

        for message in ['monthly', 'weekly', 'daily']:
            # changing the size of the columns to be bigger (that are date and volume)
            writer.sheets[message].set_column(0, 0, 25)#date
            writer.sheets[message].set_column(5, 5, 15)#volume

        writer.save()

    except:
        print("cannot create the excel file... make sure the file is not open !")
        writer.close() #close the open file that left from the try
        if os.path.exists(ExcelName):#check if the file exist if true delete it
            os.remove(ExcelName)
        raise Exception("cannot create the excel file... make sure the file is not open !")

    print("Share stock information was successfully saved in Excel file !")
    return (ExcelName, df_daily)


def Candle_Stick(Excel_File, stock, time):
    """
    Display the stock graph with candle stick and indicators by the timeframe we got from the variable "time"
    :param Excel_File: IO, Excel file path
    :param stock: String, the name of the stock
    :param time: String, the timeframe of the stock which is saved in the excel file by sheets
    :return: None
    """
    df = pd.read_excel(Excel_File, sheet_name=time)

    # Extracting Data for plotting
    ohlc = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
    ohlc['Date'] = pd.to_datetime(ohlc['Date'])
    ohlc['Date'] = ohlc['Date'].apply(date2num)
    ohlc = ohlc.astype(float)

    fig, ax = plt.subplots()

    candlestick_ohlc(ax, ohlc.values, width=0.8, colorup='green', colordown='red', alpha=0.8)

    # Setting labels & titles
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    fig.suptitle(time + ' candlestick chart of ' + stock)

    # adding grid to the graph
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)

    # Formatting Date
    date_format = DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()



    # Adding indicators
    Add_EWMA(ax, df)
    Add_Upper_and_Lower(ax, df)
    Add_MA(ax, df, time)


    fig.tight_layout()
    ax.legend(loc=0)
    plt.show()


def DateFrame_To_Excel(stock):
    """
    using yahoo API to read the stock data into dataframes,
    then we will export the data to excel file by using another method
    :param stock: string, the name of the stock
    :return: IO, excel file
    """
    try:
        df_daily = web.DataReader(stock, 'yahoo')
        df_monthly = web.get_data_yahoo(stock, interval='m')
        df_weekly = web.get_data_yahoo(stock, interval='w')
        return WriteToExcel(df_daily, df_weekly, df_monthly, stock)

    except:
        raise Exception("invalid symbol !")



stock = input("enter the stock symbol: \n").upper()
Excel_File ,df = DateFrame_To_Excel(stock)

choice = input("Please select timeframe for candle stick chart: \n1 - for daily\n2 - for weekly\n3 - for monthly\n")
if choice == "1":
    time = "daily"
elif choice == "2":
    time = "weekly"
elif choice == "3":
    time = "monthly"
else:
    print("invalid input... displaying without candle stick")

if choice == "1" or choice == "2" or choice == "3":
    Candle_Stick(Excel_File, stock, time)
    #need to add volume function !!!
    #need to add live function !!!


VisualizingChart(Excel_File, stock)

