import pandas as pd
import yfinance as yf
import datetime
import csv
import math

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding
from watchlist import watchlist

class System:
    
    #Class Variables
    RUN_DAILY = True
    PERIOD = '1y' #1d, 1mo, 3mo, 6mo, 1y
    INTERVAL = '1d'

    runningDate = ''
    capital = 10000
    equity = capital
    FEES = 8
    profit = 0
    risk = 0.5
    # minPos = capital * risk
    STOP_LOSS = 0.05
    
    toPurchase = []
    holdings = []
    valueDict = dict()

    biggestGain = 0
    biggestLoss = 0
    winners = 0
    losers = 0
    daysPassed = 0
    daysInMarket = 0

    PERF_ORDERED = False

    #Instance Variables
    def __init__(self):
        self.buyCount = 0
        self.sellCount = 0

    def run(self):
    
        stratBuilder = StrategyBuilder()
        #Retrieve stock data
        tickers = self.getStocks()

        if self.PERF_ORDERED: tickers = self.sortByPerformance(tickers, stratBuilder)

        i = 14 #Start at 14 to retrieve indicator data
        j = 0
        #Loop through each day
        while i < tickers[0].closeList.size:
            self.runningDate = tickers[0].closeList.axes[0].date[i]
            self.daysPassed += 1
            if len(self.holdings) > 0:
                self.daysInMarket += 1

            # Logging value for charting
            value = self.capital
            for holding in self.holdings:
                value += holding.units * holding.stock.closeList[i]
            self.valueDict[self.runningDate] = value

            for stock in tickers:
                
                if i < stock.closeList.size:

                    stock.setCurrentPrice(stock.closeList[i])
                    if self.STOP_LOSS > 0:
                        # Sell if hit stop loss
                        for holding in self.holdings:
                            if holding.stock.code == stock.code:
                                    
                                # if holding.stock.currentPrice <= holding.trailingStop:
                                if holding.stock.currentPrice <= holding.boughtAt * (1-self.STOP_LOSS):
                                    print('Hit stop loss for', stock.code)
                                    self.sellAsStop(holding)

                    #Get Buy/Sell result from Strategy
                    stratResult = stratBuilder.Strategy1(stock, i)
                    tradeResult = None
                    if stratResult == 'Buy':
                        tradeResult = self.buy(stock, stock.closeList[i], 1) #if self.RUN_DAILY else self.toPurchase.append(stock)
                    elif stratResult == 'Buy2':
                        tradeResult = self.buy(stock, stock.closeList[i], 0.5)
                    elif (stratResult == 'Sell') & (self.haveHolding(stock)): #& (self.toPurchase.__contains__(stock)):
                        # self.toPurchase.remove(stock)
                        tradeResult = self.sell(stock, stock.closeList[i], 1, False)
                    elif  (stratResult == 'Sell2') & (self.haveHolding(stock)):
                        tradeResult = self.sell(stock, stock.closeList[i], 0.5, False)

                    if tradeResult != None: print(tradeResult)
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print('Capital:', self.capital)

        value = self.capital
        for holding in self.holdings:
            value += holding.units * holding.stock.currentPrice

        print('Value: ', value)
        print('Profit:', self.profit)
        print('Winners:', self.winners / self.sellCount)
        print('Losers:', self.losers / self.sellCount)
        print('Biggest Gain:', self.biggestGain)
        print('Biggest Loss', self.biggestLoss)
        print('Time in Market:', self.daysInMarket / self.daysPassed)

        self.writeCSV()

    def getStocks(self):
        print('Retrieving Data...')
        stocks = []
        dailyData = yf.download(
            tickers=watchlist,
            # start='2021-01-01',
            # end='2021-02-10',
            period=self.PERIOD,
            interval=self.INTERVAL,
            group_by='ticker'
        )
                
        for stock in watchlist:
            ticker = Stock(stock)
            stocks.append(ticker)
            #Get daily data
            ticker.setData(dailyData[stock], self.INTERVAL) if len(watchlist) > 1 else ticker.setData(dailyData, self.INTERVAL)
            ticker.defineIndicators(self.INTERVAL)
        
        return stocks

    def buy(self, stock, price, allocation):
        posSize = self.positionSize(allocation)
        if posSize > 0:
            
            units = int(posSize / price)
            debit = price * units + self.FEES
            self.capital -= debit

            self.holdings.append(Holding(stock, units, price))
            self.buyCount += 1
            
            return f'{self.runningDate} : Bought {units} units of {stock.code} at {price} | {self.capital}'


    def sell(self, stock, price, allocation, noSellCond):
        units = 0
        credit = 0

        #Sell all held stocks
        for holding in self.holdings:
            if (holding.stock.code == stock.code) & ((price > holding.boughtAt) or noSellCond):
            # if (holding.stock.code == stock.code) or noSellCond:
                posSize = int(holding.units * allocation)
                units += posSize

                credit += posSize * price

                diff = (posSize * price - posSize * holding.boughtAt) - 2 * self.FEES
                self.profit += diff
                self.equity += diff

                holding.setUnits(holding.units - posSize)
                self.sellCount += 1

                if diff > 0:
                    self.winners += 1
                    if self.biggestGain < diff:
                        self.biggestGain = diff
                else:
                    self.losers += 1
                    if self.biggestLoss > diff:
                        self.biggestLoss = diff

        if units > 0:
            self.capital += credit - self.FEES

            # Remove from holdings if selling all units
            for holding in self.holdings:
                if holding.units == 0:
                    self.holdings.remove(holding)
            
        return f'{self.runningDate} : Sold {units} units of {stock.code} at {price} | {self.capital}'


    def sellAsStop(self, holding):
        diff = holding.units * holding.stock.currentPrice - holding.units * holding.boughtAt

        self.capital += holding.units * holding.stock.currentPrice
        self.profit += holding.units * holding.stock.currentPrice - holding.units * holding.boughtAt
        self.holdings.remove(holding)
        self.capital -= self.FEES
        self.profit -= self.FEES
        self.sellCount += 1
        print(self.runningDate,': Sold', holding.units, 'units of', holding.stock.code, 'at', holding.stock.currentPrice, '|', self.capital)

        if diff > 0:
            self.winners += 1
            if self.biggestGain < diff:
                self.biggestGain = diff
        else:
            self.losers += 1
            if self.biggestLoss > diff:
                self.biggestLoss = diff

    def positionSize(self, allocation):
        positionSize = (self.equity * self.risk * allocation) - self.FEES

        # # Have funds available
        # if self.capital > minPos * allocation:
        #     if positionSize < minPos:
        #         return minPos * allocation - self.FEES
        #     elif positionSize > self.capital:
        #         return self.capital - self.FEES
        #     else: 
        #         return positionSize - self.FEES
        # else:
        #     return 0

        if self.capital >= positionSize:
            return positionSize
        else:
            return 0

        

    def haveHolding(self, stock):
        for holding in self.holdings:
            if holding.stock == stock:
                return True
        
        return False

    def lowestHolding(self):
        lowest = self.holdings[0]
        for holding in self.holdings:
            if holding.stock.currentPrice * holding.units < lowest.stock.currentPrice * lowest.units:
                lowest = holding

        return lowest

    def writeCSV(self):

        with open('value.csv', 'w') as f:
            for key in self.valueDict.keys():
                f.write("%s,%s\n"%(key, self.valueDict[key]))

    def sortByPerformance(self, stocks, stratBuilder):

        # Make purchase max amount
        self.risk = 1
        perfList = dict()
        
        for stock in stocks:
            self.capital = 10000
            i = 14
            numDays = stock.closeList.size
            lastPrice = stock.closeList[0]
            while i < numDays:

                #Get Buy/Sell result from Strategy
                stratResult = stratBuilder.Strategy2(stock, i)
                
                if stratResult == 'Buy':
                    self.buy(stock, stock.closeList[i], 1)
                elif stratResult == 'Buy2':
                    self.buy(stock, stock.closeList[i], 0.5)
                elif (stratResult == 'Sell') & (self.haveHolding(stock)):
                    self.sell(stock, stock.closeList[i], 1, True)
                elif  (stratResult == 'Sell2') & (self.haveHolding(stock)):
                    self.sell(stock, stock.closeList[i], 0.5, True)

                if not math.isnan(stock.closeList[i]): lastPrice = stock.closeList[i]

                i+=1

            if self.haveHolding(stock):
                self.sell(stock, lastPrice, 1, True)

            perfList[stock] = self.capital
        
        perfList = sorted(perfList.items(), key = lambda x: x[1], reverse = True)
        perfKeys = []
        for stock in perfList:
            perfKeys.append(stock[0])
        
        self.risk = 0.1
        self.capital = 10000
        self.profit = 0
        self.holdings = []
        self.biggestGain = 0
        self.biggestLoss = 0
        self.buyCount = 0
        self.losers = 0
        self.sellCount = 0
        self.winners = 0
        return perfKeys
            
