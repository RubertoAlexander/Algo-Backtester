import yfinance as yf

class Stock:

    def __init__(self, ticker):
        self.ticker = yf.Ticker(ticker)

    def getData(self, period, interval):
        history = self.ticker.history(period, interval)
        history = history.drop(columns=['Volume', 'Dividends', 'Stock Splits'])
        self.history = history
        self.openList = history['Open']
        self.closeList = history['Close']
        self.highList = history['High']
        self.lowList = history['Low']
