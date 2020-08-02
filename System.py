import pandas as pd
import yfinance as yf
import datetime

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding

class System:
    
    #Class Variables
    RUN_DAILY = True
    runningDate = ''
    FEES = 10
    capital = 10000
    risk = 0.1
    minPos = 1000
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
            self.runningDate = tickers[0].dailyCloseList.axes[0].date[i]
            for stock in tickers:
                
                if i < stock.dailyCloseList.size:

                    #Get Buy/Sell result from Strategy
                    stratResult = stratBuilder.Strategy1(stock, i, '1d')
                    
                    if stratResult == 'Buy':
                        self.buy(stock, stock.dailyCloseList[i]) if self.RUN_DAILY else self.toPurchase.append(stock)
                    elif (stratResult == 'Sell') & (self.toPurchase.__contains__(stock)):
                        self.toPurchase.remove(stock)

                        #Sell stock if held
                        toSell = []
                        for holding in self.holdings:
                            if holding.stock == stock:
                                toSell.append(holding)
                        if len(toSell) > 0: self.sell(toSell, stock.dailyCloseList[i])

                    elif (stratResult == 'Sell') & (self.RUN_DAILY):
                        #Sell stock if held
                        toSell = []
                        for holding in self.holdings:
                            if holding.stock == stock:
                                toSell.append(holding)
                        if len(toSell) > 0: self.sell(toSell, stock.dailyCloseList[i])

                    #If cleared to purchase go through intraday indicators
                    if not self.RUN_DAILY:
                        if self.toPurchase.__contains__(stock):
                            intraday = stock.closeList.axes[0].date[j] #Intraday date

                            while intraday < self.runningDate:
                                #Move date forward if needing to
                                intraday = stock.closeList.axes[0].date[j]
                                j+=1

                            #Get Buy/Sell indicator for each interval intraday
                            while (intraday == self.runningDate) & (j < stock.closeList.axes[0].date.size):
                                intraday = stock.closeList.axes[0].date[j]

                                stratResult = stratBuilder.Strategy1(stock, j, '30m')

                                if stratResult == 'Buy':
                                    self.buy(stock, stock.closeList[j])
                                elif (stratResult == 'Sell') & (self.haveHolding(stock)):
                                    for holding in self.holdings:
                                        toSell = []
                                        if holding.stock == stock:
                                            if stock.closeList[j] > holding.boughtAt:
                                                toSell.append(holding)
                                    if len(toSell) > 0: self.sell(toSell, stock.closeList[j])

                                j+=1
                            j = 0
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print(self.capital)

        value = self.capital
        for holding in self.holdings:
            value += holding.units * holding.stock.dailyCloseList[holding.stock.dailyCloseList.size - 1]

        print('Value: ', value)

    def getStocks(self):
        print('Retrieving Data...')
        stocks = []
        dailyData = yf.download(
            tickers=self.watchlist,
            period='5y',
            interval='1d',
            group_by='ticker'
        )
        if not self.RUN_DAILY:
            intraData = yf.download(
                tickers=self.watchlist,
                period='1mo',
                interval='30m',
                group_by='ticker'
            )
                

        for stock in self.watchlist:
            ticker = Stock(stock)
            stocks.append(ticker)
            #Get daily data
            ticker.setData(dailyData[stock], '1d')
            ticker.defineIndicators('1d')

            if not self.RUN_DAILY:
                #Get intraday data
                ticker.setData(intraData[stock], '30m')
                ticker.defineIndicators('30m')
        
        return stocks

    def buy(self, stock, price):
        posSize = self.positionSize()
        if posSize > 0:
            
            units = int(posSize / price)
            self.holdings.append(Holding(stock, units, price))
            self.capital -= (price * units) + self.FEES
            self.buyCount += 1

            print(self.runningDate,': Bought', units, 'units of', stock.code, 'at', price)

    def sell(self, holdings, price):
        units = 0
        code = ''
        for holding in holdings:
            code = holding.stock.code
            units += holding.units
            self.holdings.remove(holding)

        self.capital += units * price - self.FEES
        self.sellCount += 1
        print(self.runningDate,': Sold', units, 'units of', code, 'at', price)

    def positionSize(self):
        if self.capital * self.risk < self.minPos:
            return self.minPos - self.FEES
        else: 
            return self.capital * self.risk - self.FEES

    def haveHolding(self, stock):
        for holding in self.holdings:
            if holding.stock == stock:
                return True
        
        return False
        