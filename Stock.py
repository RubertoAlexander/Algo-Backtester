import yfinance as yf
from talib._ta_lib import *

class Stock:

    def __init__(self, code):
        self.code = code
        self.ticker = yf.Ticker(code)
        self.units = 0
        self.boughtAt = 0.00
        self.greenLight = False

    def getData(self, period, interval):
        history = self.ticker.history(period, interval)
        history = history.drop(columns=['Volume', 'Dividends', 'Stock Splits'])
        
        if interval == '1d':
            self.dailyHistory = history
            self.dailyOpenList = history['Open']
            self.dailyCloseList = history['Close']
            self.dailyHighList = history['High']
            self.dailyLowList = history['Low']
        else:
            self.history = history
            self.openList = history['Open']
            self.closeList = history['Close']
            self.highList = history['High']
            self.lowList = history['Low']

    def defineIndicators(self, interval):

        if interval == '1d':
            highList = self.dailyHighList
            lowList = self.dailyLowList
            closeList = self.dailyCloseList
            self.dailyPosDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
            self.dailyNegDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
            self.dailyRSI = RSI(closeList, timeperiod=14)
            self.dailyStochk, self.dailyStochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3) 
        else:      
            highList = self.highList
            lowList = self.lowList
            closeList = self.closeList  
            self.posDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
            self.negDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
            self.rsi = RSI(closeList, timeperiod=14)
            self.stochk, self.stochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3)
