
import talib

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
        self.posDI = talib.PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        self.negDI = talib.MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
        self.rsi = talib.RSI(closeList, timeperiod=14)
        self.stochk, self.stochd = talib.STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3)

        self.wma20 = talib.WMA(closeList, timeperiod=20)
        self.wma50 = talib.WMA(closeList, timeperiod=50)
        self.wma100 = talib.WMA(closeList, timeperiod=100)
