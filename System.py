import pandas as pd
import yfinance as yf
import datetime
import csv

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding

class System:
    
    #Class Variables
    RUN_DAILY = False
    runningDate = ''
    FEES = 10
    capital = 10000
    profit = 0
    risk = 0.1
    minPos = capital * risk
    STOP_LOSS = 0

    watchlist = ['CGL.AX', 'OCL.AX', 'TNE.AX', 'BVS.AX', 'XRF.AX', 'PME.AX', 'EOS.AX', 'EOF.AX', 
                'EML.AX', 'PPS.AX', 'HUB.AX', 'APX.AX', 'WTC.AX', 'NAN.AX', 'BOT.AX', 'MVP.AX', 
                'CYP.AX', 'ALU.AX', 'ZNO.AX', 'PCK.AX', 'CUV.AX', 'IRE.AX', 'PNV.AX', 'TLX.AX', 
                'RAP.AX', 'SPL.AX', 'NEA.AX', 'ANO.AX', 'GSS.AX', 'TTB.AX', 'SKF.AX', 'MSB.AX', 
                'APT.AX', 'FLC.AX', 'KZA.AX', 'PBH.AX', 'PPH.AX', 'WSP.AX',
                'OCC.AX', 'TYR.AX', 'THC.AX', 'ADS.AX', 'LVT.AX', 'IMU.AX', 'BIT.AX', 'SWF.AX', 
                'BRN.AX', 'CDY.AX', 'RAC.AX', 'PAA.AX', 'BUD.AX', 'PIQ.AX', 'DRO.AX']

    toPurchase = []
    holdings = []

    valueDict = dict()

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
        while i < tickers[0].closeList.size:
            self.runningDate = tickers[0].closeList.axes[0].date[i]

            # Logging value for charting
            value = self.capital
            for holding in self.holdings:
                value += holding.units * holding.stock.closeList[i]
            self.valueDict[self.runningDate] = value

            for stock in tickers:
                
                if i < stock.closeList.size:

                    stock.setCurrentPrice(stock.closeList[i])
                    toSell = []
                    if self.STOP_LOSS > 0:
                        # Sell if hit stop loss
                        for holding in self.holdings:
                            if holding.stock.code == stock.code:
                                if holding.stock.currentPrice * holding.units <= holding.boughtAt * holding.units * (1-self.STOP_LOSS):
                                    print('Hit stop loss for', stock.code)
                                    toSell.append(holding)
                        if len(toSell) > 0: self.sell(toSell, stock.closeList[i])

                    #Get Buy/Sell result from Strategy
                    stratResult = stratBuilder.Strategy2(stock, i)
                    
                    if stratResult == 'Buy':
                        self.buy(stock, stock.closeList[i], 1) #if self.RUN_DAILY else self.toPurchase.append(stock)
                    elif stratResult == 'Buy2':
                        self.buy(stock, stock.closeList[i], 0.5)
                    elif (stratResult == 'Sell') & (self.haveHolding(stock)): #& (self.toPurchase.__contains__(stock)):
                        # self.toPurchase.remove(stock)

                        self.sell(stock, stock.closeList[i], 1)
                    elif  (stratResult == 'Sell2') & (self.haveHolding(stock)):
                        self.sell(stock, stock.closeList[i], 0.5)

                    # elif (stratResult == 'Sell') & (self.RUN_DAILY):
                    #     #Sell stock if greater than what was bought at
                    #     toSell = []
                    #     for holding in self.holdings:
                    #         if (holding.stock.code == stock.code) & (stock.dailyCloseList[i] > holding.boughtAt):
                    #             toSell.append(holding)
                    #     if len(toSell) > 0: self.sell(toSell, stock.dailyCloseList[i])

                    # #If cleared to purchase go through intraday indicators
                    # if not self.RUN_DAILY:
                    #     if self.toPurchase.__contains__(stock):
                    #         intraday = stock.closeList.axes[0].date[j] #Intraday date

                    #         while (intraday < self.runningDate) & (j < stock.closeList.axes[0].date.size):
                    #             #Move date forward if needing to
                    #             intraday = stock.closeList.axes[0].date[j]
                    #             j+=1

                    #         #Get Buy/Sell indicator for each interval intraday
                    #         while (intraday == self.runningDate) & (j < stock.closeList.axes[0].date.size):
                    #             stock.setCurrentPrice(stock.closeList[j])
                    #             intraday = stock.closeList.axes[0].date[j]

                    #             stratResult = stratBuilder.Strategy1(stock, j, '30m')

                    #             if stratResult == 'Buy':
                    #                 self.buy(stock, stock.closeList[j])
                    #             elif (stratResult == 'Sell') & (self.haveHolding(stock)):
                    #                 toSell = []
                    #                 for holding in self.holdings:
                    #                     if holding.stock.code == stock.code:
                    #                         if stock.closeList[j] > holding.boughtAt:
                    #                             toSell.append(holding)
                    #                 if len(toSell) > 0: self.sell(toSell, stock.closeList[j])

                    #             j+=1
                    #         j = 0
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print(self.capital)

        value = self.capital
        for holding in self.holdings:
            value += holding.units * holding.stock.closeList[holding.stock.closeList.size - 2]

        print('Value: ', value)
        print('Profit:', self.profit)

        self.writeCSV()

    def getStocks(self):
        print('Retrieving Data...')
        stocks = []
        dailyData = yf.download(
            tickers=self.watchlist,
            # start='2018-01-01',
            # end='2018-12-30',
            period='6mo',
            interval='1d',
            group_by='ticker'
        )
        if not self.RUN_DAILY:
            intraData = yf.download(
                tickers=self.watchlist,
                start='2020-06-11',
                end='2020-08-09',
                # period='1mo',
                interval='60m',
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

    def buy(self, stock, price, allocation):
        posSize = self.positionSize(allocation)
        if posSize > 0:
            
            units = int(posSize / price)
            self.holdings.append(Holding(stock, units, price))
            self.capital -= (price * units)
            self.capital -= self.FEES
            self.buyCount += 1

            print(self.runningDate,': Bought', units, 'units of', stock.code, 'at', price, '|', self.capital)


    def sell(self, stock, price, allocation):
        units = 0

        #Sell all held stocks
        for holding in self.holdings:
            if (holding.stock.code == stock.code) & (price > holding.boughtAt):
                posSize = int(holding.units * allocation)
                units += posSize
                self.capital += posSize * price
                self.profit += posSize * price - posSize * holding.boughtAt
                holding.setUnits(holding.units - posSize)

                # Remove from holdings if selling all units
                if holding.units == 0:
                    self.holdings.remove(holding)

        if units > 0:
            self.capital -= self.FEES
            self.profit -= self.FEES
            self.sellCount += 1
            print(self.runningDate,': Sold', units, 'units of', stock.code, 'at', price, '|', self.capital)

    def positionSize(self, allocation):
        equity = self.capital + self.profit
        positionSize = equity * self.risk * allocation

        # Have funds available
        if self.capital > self.minPos * allocation:
            if positionSize < self.minPos:
                return self.minPos * allocation - self.FEES
            elif positionSize > self.capital:
                return self.capital - self.FEES
            else: 
                return positionSize - self.FEES
        else:
            return 0

    def haveHolding(self, stock):
        for holding in self.holdings:
            if holding.stock == stock:
                return True
        
        return False

    def writeCSV(self):

        with open('value.csv', 'w') as f:
            for key in self.valueDict.keys():
                f.write("%s,%s\n"%(key, self.valueDict[key]))