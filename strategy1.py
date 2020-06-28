import pandas as pd
import numpy
import yfinance as yf
from talib._ta_lib import *
import tulipy as ti

ticker = yf.Ticker('APT.AX')
history = ticker.history(period='1y')
history = history.drop(columns=['Volume', 'Dividends', 'Stock Splits'])

openList = history['Open']
highList = history['High']
lowList = history['Low']
closeList = history['Close']

posDI = PLUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
negDI = MINUS_DI(high=highList, low=lowList, close=closeList, timeperiod=14)
rsi = RSI(closeList, timeperiod=14)
stochk, stochd = STOCH(high=highList, low=lowList, close=closeList, fastk_period=5, slowk_period=3, slowd_period=3)

data = {'Close': closeList, 'PosDI':posDI, 'NegDI':negDI, 'RSI':rsi, 'StochK': stochk, 'StochD':stochd}
df = pd.DataFrame(data)

print(df)

buyCount = 0
i = 14
while i < posDI.size - 1:

    isMovingPos = posDI[i] > negDI[i]
    isRSIOversold = rsi[i] < 30

    isStochKOversold = stochk[i] < 20
    isStochDOversold = stochd[i] < 20
    stochCrossedUp = (stochk[i] > stochd[i]) & (stochk[i - 1] < stochd[i - 1])

    stochBuy = isStochKOversold & isStochDOversold & stochCrossedUp

    if (isMovingPos):
        if (isRSIOversold | stochCrossedUp):
            buyCount += 1
    i+=1

print('Buys: ', buyCount)