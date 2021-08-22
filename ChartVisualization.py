import pandas as pd
import os
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import numpy as np
import yahoo_fin.stock_info as si

from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DateLocator, MONDAY

def Add_Doji(ax, df):
    Ratio_Hammer = df['Close'].mean() * 0.05
    N = len(df.index)

    Green_Doji = []
    Red_Doji = []

    for i in range(N):
        H = df['High'][i]
        C = df['Close'][i]
        O = df['Open'][i]
        L = df['Low'][i]
        # Hammer
        if (((H-L)>3*(O-C)and((C-L)/(.001+H-L)>0.6)and((O-L)/(.001+H-L)>0.6))) and O < C:
            Green_Doji.append(df['Low'][i]-1)
            Red_Doji.append(np.nan)

        # Hanging Man
        elif (((H-L)>4*(O-C))and((C-L)/(.001+H-L)>=0.75)and((O-L)/(.001+H-L)>=.075)) and C < O:
            Red_Doji.append(df['High'][i]+1)
            Green_Doji.append(np.nan)

        else:
            Green_Doji.append(np.nan)
            Red_Doji.append(np.nan)

    ax.plot(df['Date'], Green_Doji, marker='^', markersize=8, color='green', linestyle='None', alpha=0.9)
    ax.plot(df['Date'], Red_Doji, marker='v', markersize=8, color='r', linestyle='None', alpha=0.9)


def Add_Volume(ax, df, time):
    """
    Here we will define subplot that include x axis which represent dates of the stock
    y axis which will represent the volume of the stock
    :param ax: Object, subplot which will display the volume of the stock
    :param df: dictionary, dataframe
    :return: None
    """
    Number_Of_Greens = 0
    Number_Of_Reds = 0

    dates = [x for x in df['Date']]
    dates = np.asarray(dates)
    volume = [x for x in df['Volume']]
    volume = np.asarray(volume)

    width = 0.5 # value for daily
    if time == 'weekly':
        width = width * 8
    elif time == 'monthly':
        width = width * 30

    pos = df['Open'] - df['Close'] < 0
    neg = df['Open'] - df['Close'] > 0
    for i in pos:
        if i:
            Number_Of_Greens += 1
        else:
            Number_Of_Reds += 1
    print("Number of green bars: ", Number_Of_Greens)
    print("Number of red bars: ", Number_Of_Reds)

    ax.bar(dates[pos], volume[pos], color='green', width=width, align='center')
    ax.bar(dates[neg], volume[neg], color='red', width=width, align='center')

    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')

def Add_EWMA(ax, df, num=233):
    df["EWMA-"+str(num)] = df["Close"].ewm(span=num).mean()
    ax.plot(df['Date'], df["EWMA-"+str(num)] , ls='-.', label="EWMA-"+str(num), alpha=0.5)


def Add_Upper_and_Lower(ax, df, num=20):
    # upper = 13MA + 2*std(13)
    ax.plot(df['Date'], df.rolling(window=num).mean()['Close'] + 2 * df['Close'].rolling(13).std(),
            ls='--', label='Upper '+str(num), alpha=0.3)

    # lower = 13MA - 2*std(13)
    ax.plot(df['Date'], df.rolling(window=num).mean()['Close'] - 2 * df['Close'].rolling(13).std(),
            ls='--', label='Lower '+str(num), alpha=0.3)

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




def select_Path():
    """
    the function will return where the file is located in the computer according to what the user selected
    :return: String, the file path
    """
    filePath = filedialog.askdirectory()+"\\"#choosing where to locate the excel file with GUI

    if filePath == "\\": #if the user press cancel for selecting file location
        print("The file will be saved where is the python file")
        filePath = ""

    return filePath


def WriteToExcel(df_daily, df_weekly, df_monthly, stock):
    """
    here we will choose where to save our Excel file on the computer then
    we are creating excel file of the daily, weekly and monthly stock time frames in one excel when
    each time frame has a page of his own
    :return:saved excel named by the stock
    """


    ExcelName = select_Path()+stock+".xlsx"
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

    fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})

    candlestick_ohlc(ax[0], ohlc.values, width=0.8, colorup='green', colordown='red', alpha=0.8)

    # Setting labels & titles
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Price')
    fig.suptitle(time + ' candlestick chart of ' + stock)

    # adding grid to the graph
    ax[0].xaxis.grid(True)
    ax[0].yaxis.grid(True)
    ax[1].xaxis.grid(True)
    ax[1].yaxis.grid(True)

    # Formatting Date
    date_format = DateFormatter('%d-%m-%Y')
    ax[0].xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    # Adding Volume
    Add_Volume(ax[1], df, time)

    # Adding indicators
    Add_EWMA(ax[0], df)
    Add_Upper_and_Lower(ax[0], df)
    Add_MA(ax[0], df, time)
    Add_Doji(ax[0], df)

    fig.tight_layout()
    ax[0].legend(loc=0)
    plt.show()

def User_Choice():
    while True:
        choice = input("Please select timeframe: \n1 - for daily\n2 - for weekly\n3 - for monthly\n0 - to quit the program\n")

        if choice == "1":
            time = "daily"
            return choice, time
        elif choice == "2":
            time = "weekly"
            return choice, time

        elif choice == "3":
            time = "monthly"
            return choice, time

        elif choice == "0":
            print("exiting the program")
            return None, None
        else:
            print("invalid input please try again...\n")



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
        raise Exception("invalid symbol or open file!")


stock = input("enter the stock symbol: \n").upper()

Excel_File ,df = DateFrame_To_Excel(stock)

choice, time = User_Choice()

if choice == "1" or choice == "2" or choice == "3":
    print(df, "\n------------------------------\n")
    print(df.describe())
    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in si.get_quote_table(stock).items()) + "}")

    Candle_Stick(Excel_File, stock, time)
