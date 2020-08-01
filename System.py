import pandas as pd

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding

class System:
    
    #Class Variables
    FEES = 10
    capital = 10000
    minPos = 2000
    watchlist = ['CGL.AX', 'OCL.AX', 'TNE.AX', 'BVS.AX', 'XRF.AX', 'PME.AX', 'EOS.AX', 'EOF.AX', 
                'EML.AX', 'PPS.AX', 'HUB.AX', 'APX.AX', 'WTC.AX', 'NAN.AX', 'BOT.AX', 'MVP.AX', 
                'CYP.AX', 'ALU.AX', 'ZNO.AX', 'PCK.AX', 'CUV.AX', 'IRE.AX', 'PNV.AX', 'TLX.AX', 
                'RAP.AX', 'SPL.AX', 'NEA.AX', 'ANO.AX', 'GSS.AX', 'TTB.AX', 'SKF.AX', 'MSB.AX', 
                'APT.AX', 'FLC.AX', 'KZA.AX', 'PBH.AX', 'PPH.AX', 'WSP.AX', 'AVH.AX',
                'OCC.AX', 'TYR.AX', 'THC.AX', 'ADS.AX', 'LVT.AX', 'IMU.AX', 'BIT.AX', 'SWF.AX', 
                'BRN.AX', 'CDY.AX', 'RAC.AX', 'PAA.AX', 'BUD.AX', 'PIQ.AX', 'DRO.AX']


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

        i = 14 #Start at 14 to retrieve indicator data
        j = 0
        #Loop through each day
        while i < tickers[0].dailyCloseList.size:
            for stock in tickers:
                
                if i < stock.dailyCloseList.size:

                    #Get Buy/Sell result from Strategy
                    stratResult = stratBuilder.Strategy1(stock, i, '1d')
                    if stratResult == 'Buy':
                        self.toPurchase.append(stock) #Add stock to purchase once indicator hits
                    elif (stratResult == 'Sell') & (self.toPurchase.__contains__(stock)):
                        self.toPurchase.remove(stock) #Remove stock to purchase in the future

                        #Sell stock if held
                        for holding in self.holdings:
                            if holding.stock == stock:
                                self.sell(holding, stock.dailyCloseList[i])

                    day = stock.dailyCloseList.axes[0].date[i] #Date

                    #If cleared to purchase go through intraday indicators
                    if self.toPurchase.__contains__(stock):
                        intraday = stock.closeList.axes[0].date[j] #Intraday date

                        while intraday < day:
                            #Move date forward if needing to
                            intraday = stock.closeList.axes[0].date[j]
                            j+=1

                        #Get Buy/Sell indicator for each interval intraday
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
        print('Retrieving Data...')
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
        