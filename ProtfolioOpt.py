import pandas_datareader.data as web
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

plt.style.use('ggplot')

def setData():
    """
    initializing function where the user need to enter the amount of stocks and their symbol
    :return: Dataframe
    """
    symbols = []
    while True:
        num = int(input("how many stocks do you wish to enter? (the minimum is 2)\n"))
        if num > 1:
            break
        else:
            print("Error, the minimum is 2 !")

    i = 0
    while i < num:
        symbol = input("Enter symbol number {}:".format(i + 1)).upper()
        if symbol in symbols:
            print("cannot enter the same stock twice please try again...")
            i -= 1
        else:
            symbols.append(symbol)
        i += 1
    stocks = web.DataReader(symbols,'yahoo')['Adj Close']

    # Removing invalid data from invalid stocks
    df = stocks.dropna(how='all', axis=1)

    # if the number of valid stocks is not equal to num error will raise
    assert (len(df.columns)) == num, "User may have entered invalid symbols"

    return df

def ProtfolioDisplay(df):
    """
    Change the dataframe to percentage change and create a column for the equally weighted portfolio.
    Plot the normalized stock prices for comparison.
    :param df: dict, dataframe of the all close adj prices of the stocks the user entered
    """
    df['Port'] = df.mean(axis=1)
    #(df + 1).cumprod().plot()
    (df + 1).cumprod()[-1:]

    #plt.show()


def SR():
    """
    Display the sharpe ratio of the stocks and the portfolio
    Usually, any Sharpe ratio greater than 1.0 is considered acceptable to good by investors.
     A ratio higher than 2.0 is rated as very good. A ratio of 3.0 or higher is considered excellent.
      A ratio under 1.0 is considered sub-optimal.
    :return:
    """

    def sharpe_ratio(return_series, N, rf):
        """
        :param return_series:Object, Series of all the return value
        :param N: int, 252 trading days in a year
        :param rf:float, #1% risk free rate
        :return: dict, sharpe ratio
        """
        mean = return_series.mean() * N - rf
        sigma = return_series.std() * np.sqrt(N)
        return mean / sigma

    sharpes = df.apply(sharpe_ratio, args=(N, rf,), axis=0)
    # plt.ylabel('Sharpe Ratio')
    #
    # sharpes.plot.bar()
    # plt.show()
    return sharpes

def Sortino_Ratio():
    """
    Display Sortino ratio of the stocks and the portfolio.
    As a rule of thumb, a Sortino ratio of 2 and above is considered ideal.
    :return:
    """

    def sortino_ratio(series, N, rf):
        """
        :param series:
        :param N: int, 252 trading days in a year
        :param rf:float, #1% risk free rate
        :return:
        """
        mean = series.mean() * N - rf
        std_neg = series[series < 0].std() * np.sqrt(N)
        return mean / std_neg

    sortinos = df.apply(sortino_ratio, args=(N, rf,), axis=0)
    # sortinos.plot.bar()
    # plt.ylabel('Sortino Ratio')
    # plt.show()
    return sortinos


def MD():
    """
    Display the Max Drawdown of the stocks & portfolio
    The closest bar to zero is preferable
    :return:
    """

    def max_drawdown(return_series):
        """
        :param return_series:Object, Series of all the return value
        :return: int, the minimum drawdown
        """
        comp_ret = (return_series + 1).cumprod()
        peak = comp_ret.expanding(min_periods=1).max()
        dd = (comp_ret / peak) - 1
        return dd.min()

    max_drawdowns = df.apply(max_drawdown, axis=0)
    # max_drawdowns.plot.bar()
    # plt.ylabel('Max Drawdown')
    # plt.show()
    return max_drawdowns


def CR():
    """
    Calmar ratio uses max drawdown in the denominator as opposed to standard deviation.
    The higher the Calmar ratio the better with anything over 0.50 is considered to be good.
    A Calmar ratio of 3.0 to 5.0 is really good
    :return:
    """
    calmars = df.mean() * 252 / abs(MD())
    # calmars.plot.bar()
    # plt.ylabel('Calmar ratio')
    # plt.show()
    return calmars

def final_plot():
    btstats = pd.DataFrame()
    btstats['Sortino'] = Sortino_Ratio()
    btstats['Sharpe'] = SR()
    btstats['Max Drawdown'] = MD()
    btstats['Calmar'] = CR()

    (df + 1).cumprod().plot(figsize=(8, 5))
    plt.table(cellText=np.round(btstats.values, 2), colLabels=btstats.columns,
              rowLabels=btstats.index, rowLoc='center', cellLoc='center', loc='top',
              colWidths=[0.25] * len(btstats.columns))
    plt.tight_layout()
    plt.show()



stocks = setData()

df = stocks.pct_change().dropna()

N=252; rf=0.01

print("Please wait...")

ProtfolioDisplay(df)

final_plot()
