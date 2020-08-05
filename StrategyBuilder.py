
#Dummy class for building strategies
class StrategyBuilder:

    def Strategy1(self, stock, index, interval):
    
        if interval == '1d':

            indicatorArray = dict(
                                posDI=stock.dailyPosDI[index],
                                negDI=stock.dailyNegDI[index],
                                rsi=stock.dailyRSI[index],
                                stochK=stock.dailyStochk[index],
                                stochKBefore=stock.dailyStochk[index-1],
                                stochD=stock.dailyStochd[index],
                                stochDBefore=stock.dailyStochd[index-1]
                                )
        else:
            indicatorArray = dict(
                                posDI=stock.posDI[index],
                                negDI=stock.negDI[index],
                                rsi=stock.rsi[index],
                                stochK=stock.stochk[index],
                                stochKBefore=stock.stochk[index-1],
                                stochD=stock.stochd[index],
                                stochDBefore=stock.stochd[index-1]
                                )

        indicators = self.getIndicators('1', indicatorArray, index)

        if indicators.get('isMovingPos'):
            if (indicators.get('isRSIOversold') | indicators.get('stochBuy')):
                return 'Buy'
        elif (indicators.get('isRSIOversold') & indicators.get('stochBuy')):
            return 'Buy'

        if indicators.get('stochSell') | indicators.get('isRSIOverbought'):
            return 'Sell'

    def getIndicators(self, strat, indicators, index):
        if strat == '1':
            #DMI
            isMovingPos = indicators.get('posDI') > indicators.get('negDI')
            isMovingNeg = indicators.get('posDI') < indicators.get('negDI')

            #RSI
            isRSIOversold = indicators.get('rsi') < 30
            isRSIOverbought = indicators.get('rsi') > 70

            #Stochastics
            isStochKOversold = indicators.get('stochK') < 20
            isStochKOverbought = indicators.get('stochK') > 80
            isStochDOversold = indicators.get('stochD') < 20
            isStochDOverbought = indicators.get('stochD') > 80

            stochCrossedUp = (indicators.get('stochK') > indicators.get('stochD')) & (indicators.get('stochKBefore') < indicators.get('stochDBefore'))
            stochCrossedDown = (indicators.get('stochK') < indicators.get('stochD')) & (indicators.get('stochKBefore') > indicators.get('stochDBefore'))

            stochBuy = isStochKOversold & stochCrossedUp
            stochSell = isStochKOverbought & stochCrossedDown

            return dict(
                isMovingPos=isMovingPos,
                isRSIOversold=isRSIOversold,
                stochBuy=stochBuy,
                stochSell=stochSell,
                isRSIOverbought=isRSIOverbought
            )