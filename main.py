from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os
from tkinter import filedialog
import matplotlib.pyplot as plt


# import time
# import xlsxwriter
# from statistics import mean
# from tkinter import *

def VisualizingChart(Excel_File, stock):
    """
    This function will display the chart of the stock by different time frames with matplotlib
    :param Excel_File: string, The path of the excel file
    :param stock: string, Stock name
    :return: None
    """
    print("please wait building charts from excel file...")
    figure, axis = plt.subplots(2, 2) #figure is object and axis is the 2d graphs matrix
    k = 0
    arr = ['monthly', 'weekly', 'daily', '5min intraday']  # list of the time frames

    for i in axis:
        for chart in i:
            df = pd.read_excel(Excel_File, sheet_name=arr[k])# take each time different dataframe from the excel file
            chart.plot(df['date'], df['4. close'])
            chart.set_xlabel("Dates")
            chart.set_ylabel("$ Price")
            chart.set_title(stock + " " + arr[k] + " closed price")
            k += 1
    plt.tight_layout()
    plt.show()


def WriteToExcel(ts, stock):
    """
    here we will choose where to save our Excel file on the computer then
    we are creating excel file of the daily, weekly, monthly, 5min intraday stock time frames in one excel when
    each time frame has a page of his own
    :return:saved excel named by the stock
    """
    filePath = filedialog.askdirectory()+"\\"#choosing where to locate the excel file with GUI
    ExcelName = filePath+stock+".xlsx"

    try:
        writer = pd.ExcelWriter(ExcelName, engine='xlsxwriter')

        monthly_data,tmp = ts.get_monthly(symbol=stock)
        monthly_data.to_excel(writer, sheet_name='monthly')

        weekly_data,tmp = ts.get_weekly(symbol=stock)
        weekly_data.to_excel(writer, sheet_name='weekly')

        daily_data ,tmp = ts.get_daily(symbol=stock)
        daily_data.to_excel(writer, sheet_name='daily')

        five_min_data,tmp = ts.get_intraday(symbol=stock, interval='5min', outputsize='full')
        five_min_data.to_excel(writer, sheet_name='5min intraday')

        for message in ['monthly', 'weekly', 'daily', '5min intraday']:
            # changing the size of the columns to be bigger (that are date and volume)
            writer.sheets[message].set_column(0, 0, 25)#date
            writer.sheets[message].set_column(5, 5, 15)#volume

        writer.save()

    except:
        writer.close() #close the open file that left from the try
        if os.path.exists(ExcelName):#check if the file exist if true delete it
            os.remove(ExcelName)
        raise Exception("Hi this may be invalid stock!")

    print("Share stock information was successfully saved in Excel file !")
    return ExcelName


def API_To_Excel(stock):
    """
    here we got API from https://www.alphavantage.co/ that gives us data on the stock market and in order to use that data
    we need to set TimeSeries(key=API, output_format='pandas') to a variable
    after that we will read symbol of stock from the user
    """
    api_key = 'DKEJIX81H7PKJ9FJ'
    ts =TimeSeries(key=api_key, output_format='pandas')
    return WriteToExcel(ts,stock)



stock = input("enter the stock symbol: \n").upper()
Excel_File = API_To_Excel(stock)
VisualizingChart(Excel_File, stock)

