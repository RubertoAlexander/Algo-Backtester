import pandas as pd

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding

class System:
    
    #Class Variables
    FEES = 10
    capital = 10000
    minPos = 2000
    watchlist = ['AGH.AX','BIT.AX', 'BOT.AX', 'CYP.AX', 'DRO.AX', 'DW8.AX', 'IMU.AX', 'ISD.AX', 
                 'MSB.AX', 'NXS.AX', 'OCC.AX', 'PAA.AX', 'Z1P.AX']

    toPurchase = []
    holdings = []

    #Instance Variables
    def __init__(self):
        self.buyCount = 0
        self.sellCount = 0

    def run(self):
    
        stratBuilder = StrategyBuilder()
        #Retrieve stock data
        tickers = self.getStocks()

        i = 14
        j = 0
        #Loop through each day
        while i < tickers[0].dailyCloseList.size:
            for stock in tickers:

                if i < stock.dailyCloseList.size:

                    stratResult = stratBuilder.Strategy1(stock, i, '1d')
                    if stratResult == 'Buy':
                        self.toPurchase.append(stock)
                    elif (stratResult == 'Sell') & (self.toPurchase.__contains__(stock)):
                        self.toPurchase.remove(stock)

                        for holding in self.holdings:
                            if holding.stock == stock:
                                self.sell(holding, stock.dailyCloseList[i])

                    day = stock.dailyCloseList.axes[0].date[i]

                    if self.toPurchase.__contains__(stock):
                        intraday = stock.closeList.axes[0].date[j]

                        while intraday < day:
                            #Move date forward if needing to
                            intraday = stock.closeList.axes[0].date[j]
                            j+=1

                        while (intraday == day) & (j < stock.closeList.axes[0].date.size):
                            intraday = stock.closeList.axes[0].date[j]

                            stratResult = stratBuilder.Strategy1(stock, j, '5m')

                            if stratResult == 'Buy':
                                self.buy(stock, stock.closeList[j])
                            elif (stratResult == 'Sell') & (self.haveHolding(stock)):
                                for holding in self.holdings:
                                    if holding.stock == stock:
                                        if stock.closeList[j] > holding.boughtAt:
                                            self.sell(holding, stock.closeList[j])

                            j+=1
                        j = 0
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print(self.capital)

        value = self.capital
        for holding in self.holdings:
            value += holding.units * holding.stock.closeList[holding.stock.closeList.size - 1]

        print('Value: ', value)

    def getStocks(self):
        stocks = []
        for stock in self.watchlist:
            ticker = Stock(stock)
            stocks.append(ticker)
            #Get daily data
            ticker.getData('3mo', '1d')
            ticker.defineIndicators('1d')

            #Get intraday data
            ticker.getData('1mo', '5m')
            ticker.defineIndicators('5m')
        
        return stocks

    def getGreenLight(self, stock, index):
        #DMI
        isMovingPos = stock.dailyPosDI[index] > stock.dailyNegDI[index]
        isMovingNeg = stock.dailyPosDI[index] < stock.dailyNegDI[index]

        #RSI
        isRSIOversold = stock.dailyRSI[index] < 30
        isRSIOverbought = stock.dailyRSI[index] > 70

        #Stochastics
        isStochKOversold = stock.dailyStochk[index] < 20
        isStochKOverbought = stock.dailyStochk[index] > 80
        isStochDOversold = stock.dailyStochd[index] < 20
        isStochDOverbought = stock.dailyStochd[index] > 80

        stochCrossedUp = (stock.dailyStochk[index] > stock.dailyStochd[index]) & (stock.dailyStochk[index - 1] < stock.dailyStochd[index - 1])
        stochCrossedDown = (stock.dailyStochk[index] < stock.dailyStochd[index]) & (stock.dailyStochk[index - 1] > stock.dailyStochd[index - 1])

        stochBuy = isStochKOversold & stochCrossedUp
        stochSell = isStochKOverbought & stochCrossedDown

        if isMovingPos:
            if (isRSIOversold | stochBuy):
                return 'Buy'
        elif (isRSIOversold & stochBuy):
            return 'Buy'

        if stochSell | isRSIOverbought:
            return 'Sell'

    def buy(self, stock, price):
        posSize = self.positionSize()
        if posSize > 0:
            
            units = int(posSize / price)
            self.holdings.append(Holding(stock, units, price))
            self.capital -= (price * units) + self.FEES
            self.buyCount += 1

            print('Bought', units, 'units of', stock.code, 'at', price)
            print('Capital: ', self.capital)

    def sell(self, holding, price):
        self.capital += holding.units * price - self.FEES
        self.holdings.remove(holding)

        print('Sold', holding.units, 'units of', holding.stock.code, 'at', price)
        print('Capital:', self.capital)
        self.sellCount += 1

    def positionSize(self):
        if self.capital < self.minPos:
            return 0
        else: 
            return self.minPos - self.FEES

    def haveHolding(self, stock):
        for holding in self.holdings:
            if holding.stock == stock:
                return True
        
        return False
        