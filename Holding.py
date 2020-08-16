
class Holding:
    
    def __init__(self, stock, units, price):
        self.stock = stock
        self.units = units
        self.boughtAt = price
        self.trailingStop = 0

    def setUnits(self, units):
        self.units = units

    def setTrailingStop(self, price):
        self.trailingStop = price
        
        