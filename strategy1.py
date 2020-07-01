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

        self.watchlist = ['AGH.AX', 'BIT.AX', 'BOT.AX', 'CYP.AX', 'DRO.AX', 'DW8.AX', 'IMU.AX', 'ISD.AX', 
                        'MSB.AX', 'NXS.AX', 'OCC.AX', 'PAA.AX', 'RAP.AX', 'Z1P.AX']

    def buy(self, code, price):
        self.boughtAt = price
        self.units = int(self.capital / price)
        self.capital -= self.boughtAt * self.units
        self.buyCount += 1
        self.positionOpen = code
        print('Bought', self.units, 'units of', code, 'at', price)

    def sell(self, price):
        self.capital += self.units * price
        self.sellCount += 1
        self.positionOpen = ''
        print('Sold', self.units, 'units at', price)

    def run(self):

        tickers = []
        for stock in self.watchlist:
            ticker = Stock(stock)
            tickers.append(ticker)
            ticker.getData('1mo', '15m')
            ticker.defineIndicators()

        i = 14
        print(tickers[0].closeList.size)
        
        while i < tickers[0].closeList.size - 1:
            for stock in tickers:

                if i < stock.closeList.size:

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
                                self.buy(stock.code, stock.closeList[i])
                    elif (isRSIOversold & stochBuy):
                        if not self.positionOpen:
                            self.buy(stock.code, stock.closeList[i])

                    #Sell Indicator
                    if self.positionOpen == stock.code:
                        if stochSell | isRSIOverbought:
                            if stock.closeList[i] > self.boughtAt:
                                self.sell(stock.closeList[i])
                        # elif stock.closeList.index[i].hour == 15:
                        #     self.sell(stock.closeList[i])

            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print(self.capital + self.boughtAt * self.units)