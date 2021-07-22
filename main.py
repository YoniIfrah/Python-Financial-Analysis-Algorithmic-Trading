import pandas as pd
import os
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas_datareader.data as web




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

            #chart.plot.bar(df['Date'], df['Volume'], linewidth=1, label='Close', alpha=0.1)


            #upper = 13MA + 2*std(13)
            chart.plot(df['Date'], df.rolling(window=13).mean()['Close'] + 2*df['Close'].rolling(13).std(),ls='--', label='Upper', alpha=0.3)

            #lower = 13MA - 2*std(13)
            chart.plot(df['Date'], df.rolling(window=13).mean()['Close'] - 2*df['Close'].rolling(13).std(), ls='--', label='Lower', alpha=0.3)

            if arr[k] == 'weekly' or arr[k] == 'daily':
                # MA of 34 closes
                chart.plot(df['Date'], df.rolling(window=34).mean()['Close'], label='Close 34 MA', alpha=0.7, linewidth=0.5)
                # MA of 55 closes
                chart.plot(df['Date'], df.rolling(window=55).mean()['Close'], label='Close 55 MA', alpha=0.7, linewidth=0.5)

                if arr[k] == 'daily':
                    # MA of 233 closes
                    chart.plot(df['Date'], df.rolling(window=233).mean()['Close'], label='Close 233 MA', alpha=0.7, linewidth=0.5)
                else:
                    # MA of 13 closes
                    chart.plot(df['Date'], df.rolling(window=13).mean()['Close'], label='Close 13 MA', alpha=0.7, linewidth=0.5)


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

        df_monthly.to_excel(writer, sheet_name='monthly')

        df_weekly.to_excel(writer, sheet_name='weekly')

        df_daily.to_excel(writer, sheet_name='daily')


        for message in ['monthly', 'weekly', 'daily']:
            # changing the size of the columns to be bigger (that are date and volume)
            writer.sheets[message].set_column(0, 0, 25)#date
            writer.sheets[message].set_column(5, 5, 15)#volume

        writer.save()

    except:
        writer.close() #close the open file that left from the try
        if os.path.exists(ExcelName):#check if the file exist if true delete it
            os.remove(ExcelName)
        raise Exception("cannot create the excel file... make sure the file is not open !")

    print("Share stock information was successfully saved in Excel file !")
    return (ExcelName, df_daily)


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
        raise Exception("invalid stock symbol !")



stock = input("enter the stock symbol: \n").upper()
Excel_File ,df = DateFrame_To_Excel(stock)
VisualizingChart(Excel_File, "stock")

