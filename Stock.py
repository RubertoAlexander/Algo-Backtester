import yfinance as yf
from talib._ta_lib import *

class Stock:

    def __init__(self, code):
        self.code = code
        self.ticker = yf.Ticker(code)
        self.units = 0
        self.boughtAt = 0.00

    def getData(self, period, interval):
        history = self.ticker.history(period, interval)
        history = history.drop(columns=['Volume', 'Dividends', 'Stock Splits'])
        self.history = history
        self.openList = history['Open']
        self.closeList = history['Close']
        self.highList = history['High']
        self.lowList = history['Low']

    def defineIndicators(self):
        highList = self.highList
        lowList = self.lowList
        closeList = self.closeList
        
        self.posDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        self.negDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        self.rsi = RSI(closeList, timeperiod=14)
        self.stochk, self.stochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3)
