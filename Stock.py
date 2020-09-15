
from talib._ta_lib import *

class Stock:

    def __init__(self, code):
        self.code = code
        self.greenLight = False

    def setCurrentPrice(self, price):
        self.currentPrice = price        

    def setData(self, data, interval):
        
        self.history = data
        self.openList = data['Open']
        self.closeList = data['Close']
        self.highList = data['High']
        self.lowList = data['Low']

    def defineIndicators(self, interval):

        highList = self.highList
        lowList = self.lowList
        closeList = self.closeList  
        self.posDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        self.negDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        self.rsi = RSI(closeList, timeperiod=14)
        self.stochk, self.stochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3)
