import pandas as pd
import yfinance as yf
import datetime
import csv

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding
from watchlist import watchlist

class System:
    
    #Class Variables
    RUN_DAILY = True
    PERIOD = '3mo' #1d, 1mo, 3mo, 6mo, 1y
    INTERVAL = '1d'

    runningDate = ''
    FEES = 10
    capital = 10000
    profit = 0
    risk = 0.1
    minPos = capital * risk
    STOP_LOSS = 0.5
    
    toPurchase = []
    holdings = []
    valueDict = dict()

    biggestGain = 0
    biggestLoss = 0
    winners = 0
    losers = 0
    daysPassed = 0
    daysInMarket = 0

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
                    
                    if stratResult == 'Buy':
                        print(self.runningDate, 'Buy', stock.code)
                        self.buy(stock, stock.closeList[i], 1) #if self.RUN_DAILY else self.toPurchase.append(stock)
                    elif stratResult == 'Buy2':
                        self.buy(stock, stock.closeList[i], 0.5)
                    elif (stratResult == 'Sell') & (self.haveHolding(stock)): #& (self.toPurchase.__contains__(stock)):
                        # self.toPurchase.remove(stock)
                        print(self.runningDate, 'Sell', stock.code)
                        self.sell(stock, stock.closeList[i], 1)
                    elif  (stratResult == 'Sell2') & (self.haveHolding(stock)):
                        self.sell(stock, stock.closeList[i], 0.5)
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print('Capital:', self.capital)

        value = self.capital
        for holding in self.holdings:
            value += holding.units * holding.stock.currentPrice

        print('Value: ', value)
        print('Profit:', self.profit)
        print('Winners:', self.winners / self.buyCount)
        print('Losers:', self.losers / self.buyCount)
        print('Biggest Gain:', self.biggestGain)
        print('Biggest Loss', self.biggestLoss)
        print('Time in Market:', self.daysInMarket / self.daysPassed)

        self.writeCSV()

    def getStocks(self):
        print('Retrieving Data...')
        stocks = []
        dailyData = yf.download(
            tickers=watchlist,
            # start='2019-01-01',
            # end='2019-12-30',
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

                diff = posSize * price - posSize * holding.boughtAt

                self.capital += posSize * price
                self.profit += posSize * price - posSize * holding.boughtAt
                holding.setUnits(holding.units - posSize)

                # Remove from holdings if selling all units
                if holding.units == 0:
                    self.holdings.remove(holding)

                if diff > 0:
                    self.winners += 1
                    if self.biggestGain < diff:
                        self.biggestGain = diff
                else:
                    self.losers += 1
                    if self.biggestLoss > diff:
                        self.biggestLoss = diff

        if units > 0:
            self.capital -= self.FEES
            self.profit -= self.FEES
            self.sellCount += 1
            print(self.runningDate,': Sold', units, 'units of', stock.code, 'at', price, '|', self.capital)


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