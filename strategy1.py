from talib._ta_lib import *
import tulipy as ti
import pandas as pd

from Stock import Stock

class Strategy:
    
    def __init__(self):
        self.buyCount = 0
        self.sellCount = 0
        self.capital = 5000
        self.positionOpen = False
        self.units = 0
        self.boughtAt = 0.00

        self.watchlist = ['APT.AX', 'Z1P.AX', 'MSB.AX']

    def defineIndicators(self, stock):
        stock.posDI = PLUS_DI(high=stock.highList, low=stock.lowList, close=stock.closeList, timeperiod=14)
        stock.negDI = MINUS_DI(high=stock.highList, low=stock.lowList, close=stock.closeList, timeperiod=14)
        stock.rsi = RSI(stock.closeList, timeperiod=14)
        stock.stochk, stock.stochd = STOCH(high=stock.highList, low=stock.lowList, close=stock.closeList, fastk_period=5, slowk_period=3, slowd_period=3)

    # data = {'Close': stock.closeList, 'PosDI':posDI, 'NegDI':negDI, 'RSI':rsi, 'StochK': stochk, 'StochD':stochd}
    # df = pd.DataFrame(data)

    # print(df)

    def buy(self, price):
        self.boughtAt = price
        self.units = int(self.capital / price)
        self.capital -= self.boughtAt * self.units
        self.buyCount += 1
        self.positionOpen = True
        print('Bought ', self.units, ' units at ', price)

    def sell(self, price):
        self.capital += self.units * price
        self.sellCount += 1
        self.positionOpen = False
        print('Sold ', self.units, ' units at ', price)

    def run(self):

        tickers = []
        for stock in self.watchlist:
            ticker = Stock(stock)
            tickers.append(ticker)
            ticker.getData('1mo', '5m')
            self.defineIndicators(ticker)

        i = 14
        while i < tickers[0].closeList.size:

            j = 0
            for stock in tickers:

                #DMI
                isMovingPos = stock.posDI[i] > stock.negDI[i]
                isMovingNeg = stock.posDI[i] < stock.negDI[i]

                #RSI
                isRSIOversold = stock.rsi[i] < 30
                isRSIOverbought = stock.rsi[i] > 70

                #Stochastics
                isStochKOversold = stock.stochk[i] < 20
                isStochKOverbought = stock.stochk[i] > 80
                isStochDOversold = stock.stochd[i] < 20
                isStochDOverbought = stock.stochd[i] > 80

                stochCrossedUp = (stock.stochk[i] > stock.stochd[i]) & (stock.stochk[i - 1] < stock.stochd[i - 1])
                stochCrossedDown = (stock.stochk[i] < stock.stochd[i]) & (stock.stochk[i - 1] > stock.stochd[i - 1])

                stochBuy = isStochKOversold & isStochDOversold & stochCrossedUp
                stochSell = isStochKOverbought & isStochDOverbought & stochCrossedDown

                #Buy Indicator
                if isMovingPos:
                    if (isRSIOversold | stochCrossedUp):
                        if not self.positionOpen:
                            self.buy(stock.closeList[i])
                elif (isRSIOversold & stochBuy):
                    if not self.positionOpen:
                        self.buy(stock.closeList[i])

                #Sell Indicator
                if stochSell | isRSIOverbought:
                    if self.positionOpen & (stock.closeList[i] > self.boughtAt):
                        self.sell(stock.closeList[i])
                # elif self.positionOpen & (self.stock.closeList.index[i].hour == 15):
                #     self.sell(self.stock.closeList[i])
                j+=1
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print(self.capital + self.boughtAt * self.units)