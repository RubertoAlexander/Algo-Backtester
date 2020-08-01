
#Dummy class for building strategies
class StrategyBuilder:

    def Strategy1(self, stock, index, interval):

        return 'Sell'

    def getIndicators(self, strat, indicators, index):
        return False