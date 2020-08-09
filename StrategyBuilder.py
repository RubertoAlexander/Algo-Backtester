
#Dummy class for building strategies
class StrategyBuilder:

    def Strategy1(self, stock, index):
    
        # if interval == '1d':

        #     indicatorArray = dict(
        #                         posDI=stock.dailyPosDI[index],
        #                         negDI=stock.dailyNegDI[index],
        #                         rsi=stock.dailyRSI[index],
        #                         stochK=stock.dailyStochk[index],
        #                         stochKBefore=stock.dailyStochk[index-1],
        #                         stochD=stock.dailyStochd[index],
        #                         stochDBefore=stock.dailyStochd[index-1]
        #                         )
        # else:
        #     indicatorArray = dict(
        #                         posDI=stock.posDI[index],
        #                         negDI=stock.negDI[index],
        #                         rsi=stock.rsi[index],
        #                         stochK=stock.stochk[index],
        #                         stochKBefore=stock.stochk[index-1],
        #                         stochD=stock.stochd[index],
        #                         stochDBefore=stock.stochd[index-1]
        #                         )

        # indicators = self.getIndicators('1', indicatorArray, index)

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
        stochKGreaterD = stock.stochk[index] > stock.stochd[index]

        stochCrossedUp = (stock.stochk[index] > stock.stochd[index]) & (stock.stochk[index-1] < stock.stochd[index-1])
        stochCrossedDown = (stock.stochk[index] < stock.stochd[index]) & (stock.stochk[index-1] > stock.stochd[index-1])

        stochBuy = (isStochDOversold & stochCrossedUp)
        stochSell = (isStochDOverbought & stochCrossedDown)

        if isMovingPos:
            if (isRSIOversold | stochBuy):
                return 'Buy'
        elif (isRSIOversold & stochBuy):
            return 'Buy'

        if stochSell:
            return 'Sell'
        elif isRSIOverbought: #& (not indicators.get('isStochKOverbought')) & indicators.get('stochKGreaterD'):
            if not isStochKOverbought:
                return 'Sell'

    def Strategy2(self, stock, index):

        #Stochastics
        isStochKOversold = stock.stochk[index] < 20
        isStochKOverbought = stock.stochk[index] > 80
        isStochDOversold = stock.stochd[index] < 20
        isStochDOverbought = stock.stochd[index] > 80

        stochCrossedUp = (stock.stochk[index] > stock.stochd[index]) & (stock.stochk[index-1] < stock.stochd[index-1])
        stochCrossedDown = (stock.stochk[index] < stock.stochd[index]) & (stock.stochk[index-1] > stock.stochd[index-1])

        if stochCrossedUp: 
            if isStochDOversold:
                return 'Buy'
            elif stock.stochd[index] < 40:
                return 'Buy2'
        elif stochCrossedDown:
            if isStochDOverbought:
                return 'Sell'
            elif stock.stochd[index] > 60:
                return 'Sell2'
        

    # def getIndicators(self, strat, indicators, index):
    #     if strat == '1':
    #         #DMI
    #         isMovingPos = indicators.get('posDI') > indicators.get('negDI')
    #         isMovingNeg = indicators.get('posDI') < indicators.get('negDI')

    #         #RSI
    #         isRSIOversold = indicators.get('rsi') < 30
    #         isRSIOverbought = indicators.get('rsi') > 70

    #         #Stochastics
    #         isStochKOversold = indicators.get('stochK') < 20
    #         isStochKOverbought = indicators.get('stochK') > 80
    #         isStochDOversold = indicators.get('stochD') < 20
    #         isStochDOverbought = indicators.get('stochD') > 80
    #         stochKGreaterD = indicators.get('stochK') > indicators.get('stochD')

    #         stochCrossedUp = (indicators.get('stochK') > indicators.get('stochD')) & (indicators.get('stochKBefore') < indicators.get('stochDBefore'))
    #         stochCrossedDown = (indicators.get('stochK') < indicators.get('stochD')) & (indicators.get('stochKBefore') > indicators.get('stochDBefore'))

    #         stochBuy = (isStochDOversold & stochCrossedUp)
    #         stochSell = (isStochDOverbought & stochCrossedDown)

    #         return dict(
    #             isMovingPos=isMovingPos,
    #             isRSIOversold=isRSIOversold,
    #             isStochKOverbought=isStochKOverbought,
    #             stochKGreaterD=stochKGreaterD,
    #             stochBuy=stochBuy,
    #             stochSell=stochSell,
    #             isRSIOverbought=isRSIOverbought
    #         )