
class StrategyBuilder:

    def Strategy1(self, stock, index, interval):

        if interval == '1d':
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
        else:
            #DMI
            isMovingPos = stock.posDI[index] > stock.negDI[index]
            isMovingNeg = stock.posDI[index] < stock.negDI[index]

            #RSI
            isRSIOversold = stock.rsi[index] < 30
            isRSIOverbought = stock.rsi[index] > 70

            #Stochastics
            isStochKOversold = stock.stochk[index] < 20
            isStochKOverbought = stock.stochk[index] > 80
            isStochDOversold = stock.stochd[index] < 20
            isStochDOverbought = stock.stochd[index] > 80

            stochCrossedUp = (stock.stochk[index] > stock.stochd[index]) & (stock.stochk[index - 1] < stock.stochd[index - 1])
            stochCrossedDown = (stock.stochk[index] < stock.stochd[index]) & (stock.stochk[index - 1] > stock.stochd[index - 1])

        stochBuy = isStochKOversold & stochCrossedUp
        stochSell = isStochKOverbought & stochCrossedDown

        if isMovingPos:
            if (isRSIOversold | stochBuy):
                return 'Buy'
        elif (isRSIOversold & stochBuy):
            return 'Buy'

        if stochSell | isRSIOverbought:
            return 'Sell'