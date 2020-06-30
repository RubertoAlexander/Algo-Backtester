import pandas as pd
import numpy
import yfinance as yf
from talib._ta_lib import *
import tulipy as ti

ticker = yf.Ticker('MSB.AX')
history = ticker.history(period='1mo', interval='5m')
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
sellCount = 0

capital = 5000
positionOpen = False
units = 0
boughtAt = 0.00


i = 14
while i < closeList.size:

    #DMI
    isMovingPos = posDI[i] > negDI[i]
    isMovingNeg = posDI[i] < negDI[i]

    #RSI
    isRSIOversold = rsi[i] < 30
    isRSIOverbought = rsi[i] > 70

    #Stochastics
    isStochKOversold = stochk[i] < 20
    isStochKOverbought = stochk[i] > 80
    isStochDOversold = stochd[i] < 20
    isStochDOverbought = stochd[i] > 80

    stochCrossedUp = (stochk[i] > stochd[i]) & (stochk[i - 1] < stochd[i - 1])
    stochCrossedDown = (stochk[i] < stochd[i]) & (stochk[i - 1] > stochd[i - 1])

    stochBuy = isStochKOversold & isStochDOversold & stochCrossedUp
    stochSell = isStochKOverbought & isStochDOverbought & stochCrossedDown

    #Buy Indicator
    if isMovingPos:
        if (isRSIOversold | stochCrossedUp):
            if not positionOpen:
                boughtAt = closeList[i]
                units = int(capital / boughtAt)
                capital -= boughtAt * units
                buyCount += 1
                positionOpen = True
    elif (isRSIOversold & stochBuy):
        if not positionOpen:
            boughtAt = closeList[i]
            units = int(capital / boughtAt)
            capital -= boughtAt * units
            buyCount += 1
            positionOpen = True

    if stochSell | isRSIOverbought:
        if positionOpen & (closeList[i] > boughtAt):
            boughtAt = 0
            capital += units * closeList[i]
            sellCount += 1
            positionOpen = False
    elif positionOpen & (closeList.index[i].hour == 15):
        boughtAt = 0
        capital += units * closeList[i]
        sellCount += 1
        positionOpen = False
    i+=1

print('Buys: ', buyCount, '\n', 'Sells: ', sellCount)
print(capital)