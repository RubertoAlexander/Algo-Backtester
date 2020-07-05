import pandas as pd

from Stock import Stock

class Strategy:
    
    FEES = 10

    def __init__(self):
        self.buyCount = 0
        self.sellCount = 0
        self.capital = 5000
        self.risk = 0.1
        self.maxPosition = 5000

        self.watchlist = ['AGH.AX', 'BIT.AX', 'BOT.AX', 'CYP.AX', 'DRO.AX', 'DW8.AX', 'IMU.AX', 'ISD.AX', 
                        'MSB.AX', 'NXS.AX', 'OCC.AX', 'PAA.AX', 'RAP.AX', 'Z1P.AX']
        self.positions = {}

    def run(self):

        tickers = []
        for stock in self.watchlist:
            ticker = Stock(stock)
            tickers.append(ticker)
            ticker.getData('1y', '1d')
            ticker.defineIndicators()

        i = 14
        print(tickers[0].closeList.size)
        
        while i < tickers[0].closeList.size:
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

                    stochBuy = isStochKOversold & stochCrossedUp
                    stochSell = isStochKOverbought & stochCrossedDown

                    #Buy Indicator
                    if self.capital >= 500 & stock.units == 0:
                        if isMovingPos:
                            if (isRSIOversold | stochBuy):
                                self.buy(stock, stock.closeList[i])
                        elif (isRSIOversold & stochBuy):
                            self.buy(stock, stock.closeList[i])

                    #Sell Indicator
                    if stock.units > 0:
                        if stochSell | isRSIOverbought:
                            if stock.closeList[i] > stock.boughtAt:
                                self.sell(stock, stock.closeList[i])
                        # elif stock.closeList.index[i].hour == 15:
                        #     self.sell(stock.closeList[i])

                        # if i == stock.closeList.size - 1:
                        #     self.sell(stock, stock.closeList[i])
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print(self.capital)

        value = self.capital
        for stock in tickers:
            value += stock.units * stock.closeList[stock.closeList.size - 1]

        print('Value: ', value)

    def buy(self, stock, price):
        stock.boughtAt = price
        stock.units = int(self.positionSize() / price) + 1
        self.capital -= (price * stock.units) + self.FEES
        self.buyCount += 1
        self.positionOpen = True
        #self.positions[code] = {price: units}
        print('Bought', stock.units, 'units of', stock.code, 'at', price)
        print('Capital: ', self.capital)

    def sell(self, stock, price):
        self.capital += stock.units * price - self.FEES
        print('Sold', stock.units, 'units of', stock.code, 'at', price)
        print('Capital:', self.capital)
        stock.boughtAt = 0.00
        stock.units = 0
        self.sellCount += 1
        self.positionOpen = False

    def positionSize(self):
        if self.capital > 500:
            if self.capital * self.risk > 500:
                return self.capital * risk
            else: return 500
        else: return 0
        