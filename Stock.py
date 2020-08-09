
from talib._ta_lib import *

class Stock:

    def __init__(self, code):
        self.code = code
        self.greenLight = False

    def setCurrentPrice(self, price):
        self.currentPrice = price        

    def setData(self, data, interval):
        
        # if interval == '1d':
        #     self.dailyHistory = data
        #     self.dailyOpenList = data['Open']
        #     self.dailyCloseList = data['Close']
        #     self.dailyHighList = data['High']
        #     self.dailyLowList = data['Low']
        # else:
            self.history = data
            self.openList = data['Open']
            self.closeList = data['Close']
            self.highList = data['High']
            self.lowList = data['Low']

    def defineIndicators(self, interval):

        # if interval == '1d':
        #     highList = self.dailyHighList
        #     lowList = self.dailyLowList
        #     closeList = self.dailyCloseList
        #     self.dailyPosDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        #     self.dailyNegDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        #     self.dailyRSI = RSI(closeList, timeperiod=14)
        #     self.dailyStochk, self.dailyStochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3) 
        # else:      
            highList = self.highList
            lowList = self.lowList
            closeList = self.closeList  
            self.posDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
            self.negDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
            self.rsi = RSI(closeList, timeperiod=14)
            self.stochk, self.stochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3)
