
class Holding:
    
    def __init__(self, stock, units, price):
        self.stock = stock
        self.units = units
        self.boughtAt = price

    def setUnits(self, units):
        self.units = units
        
        