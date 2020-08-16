import pandas as pd
import yfinance as yf
import datetime
import csv

from StrategyBuilder import StrategyBuilder
from Stock import Stock
from Holding import Holding

class System:
    
    #Class Variables
    RUN_DAILY = True
    runningDate = ''
    FEES = 10
    capital = 10000
    profit = 0
    risk = 0.25
    minPos = capital * risk
    STOP_LOSS = 0.5

    # watchlist = ['OCL.AX', 'TNE.AX', 'CGL.AX', 'BVS.AX', 'XRF.AX', 'PME.AX', 'EML.AX', 'PPS.AX', 'EOS.AX', 'EOF.AX', 'CLA.AX', 'HUB.AX', 'WTC.AX', 'NAN.AX', 'BOT.AX', 'APX.AX', 'MVP.AX', 'ALU.AX', 'PCK.AX', 'CUV.AX', 'IRE.AX', 'ZNO.AX', 'PNV.AX', 'TLX.AX', 'RAP.AX', 'SPL.AX', 'TTB.AX', 'GSS.AX', 'FLC.AX', 'NEA.AX', 'SKF.AX', 'MSB.AX', 'APT.AX', 'IPD.AX', 'PBH.AX', 'PPH.AX', 'KZA.AX', 'WSP.AX', 'AVH.AX', 'PAR.AX', 'OCC.AX', 'Z1P.AX', 'TYR.AX', 'THC.AX', 'CYP.AX', 'LVT.AX', 'ANO.AX', 'PTX.AX', 'HWH.AX', 'DW8.AX', 'IMU.AX', 'BIT.AX', 'SWF.AX', 'BRN.AX', 'RAC.AX', 'AR9.AX', 'NUH.AX', 'RCE.AX', 'ANP.AX', 'PAA.AX', 'IMC.AX', 'OSX.AX', 'PIQ.AX', 'IBX.AX', 'DXB.AX', 'VR1.AX']
    watchlist = ['OCL.AX', 'TNE.AX', 'CGL.AX', 'BVS.AX', 'XRF.AX', 'PME.AX', 'EML.AX', 'PPS.AX', 'EOS.AX', 'CLA.AX', 'HUB.AX', 'WTC.AX', 'NAN.AX', 'BOT.AX', 'APX.AX', 'MVP.AX', 'ALU.AX', 'PCK.AX', 'CUV.AX', 'IRE.AX', 'ZNO.AX', 'PNV.AX', 'TLX.AX', 'RAP.AX', 'SPL.AX', 'TTB.AX', 'GSS.AX', 'FLC.AX', 'NEA.AX', 'SKF.AX', 'MSB.AX', 'APT.AX', 'IPD.AX', 'PPH.AX', 'KZA.AX', 'PAR.AX', 'OCC.AX', 'Z1P.AX', 'THC.AX', 'CYP.AX', 'LVT.AX', 'ANO.AX', 'PTX.AX', 'HWH.AX', 'DW8.AX', 'IMU.AX', 'BIT.AX', 'SWF.AX', 'BRN.AX', 'RAC.AX', 'AR9.AX', 'NUH.AX', 'RCE.AX', 'ANP.AX', 'PAA.AX', 'IMC.AX', 'PIQ.AX', 'IBX.AX', 'DXB.AX', 'VR1.AX']

    #watchlist =['A2M.AX', 'AAC.AX', 'ABC.AX', 'ABP.AX', 'AFI.AX', 'AGL.AX', 'AIA.AX', 'ALD.AX', 'ALL.AX', 'ALQ.AX', 'ALU.AX', 'ALX.AX', 'AMC.AX', 'AMP.AX', 'ANN.AX', 'ANZ.AX', 'APA.AX', 'API.AX', 'APT.AX', 'APX.AX', 'ARB.AX', 'ARF.AX', 'ARG.AX', 'ASB.AX', 'AST.AX', 'ASX.AX', 'AVH.AX', 'AWC.AX', 'AX1.AX', 'AZJ.AX', 'BAP.AX', 'BBN.AX', 'BEN.AX', 'BGA.AX', 'BHP.AX', 'BIN.AX', 'BKL.AX', 'BKW.AX', 'BLD.AX', 'BLX.AX', 'BOQ.AX', 'BPT.AX', 'BRG.AX', 'BSL.AX', 'BVS.AX', 'BWP.AX', 'BXB.AX', 'CAR.AX', 'CBA.AX', 'CCL.AX', 'CCP.AX', 'CCX.AX', 'CGC.AX', 'CGF.AX', 'CHC.AX', 'CIM.AX', 'CKF.AX', 'CNU.AX', 'COH.AX', 'COL.AX', 'CPU.AX', 'CQR.AX', 'CSL.AX', 'CSR.AX', 'CTD.AX', 'CUV.AX', 'CWN.AX', 'CWY.AX', 'DHG.AX', 'DMP.AX', 'DOW.AX', 'DXS.AX', 'ECX.AX', 'EHE.AX', 'EHL.AX', 'ELD.AX', 'EML.AX', 'EVN.AX', 'FBU.AX', 'FLT.AX', 'FMG.AX', 'FNP.AX', 'FPH.AX', 'FXL.AX', 'GMA.AX', 'GMG.AX', 'GOR.AX', 'GOZ.AX', 'GPT.AX', 'GUD.AX', 'GWA.AX', 'HLS.AX', 'HSN.AX', 'HVN.AX', 'IAG.AX', 'IEL.AX', 'IEM.AX', 'IEU.AX', 'IFL.AX', 'IGO.AX', 'ILU.AX', 'IMD.AX', 'INA.AX', 'ING.AX', 'IPH.AX', 'IPL.AX', 'IRE.AX', 'IRI.AX', 'IVC.AX', 'IVV.AX', 'JBH.AX', 'JHG.AX', 'JHX.AX', 'KGN.AX', 'KLA.AX', 'LLC.AX', 'LNK.AX', 'LOV.AX', 'LYC.AX', 'MFG.AX', 'MGR.AX', 'MIN.AX', 'MMS.AX', 'MND.AX', 'MNF.AX', 'MP1.AX', 'MPL.AX', 'MQG.AX', 'MSB.AX', 'MTS.AX', 'NAB.AX', 'NAN.AX', 'NCM.AX', 'NEA.AX', 'NEC.AX', 'NHC.AX', 'NHF.AX', 'NSR.AX', 'NST.AX', 'NUF.AX', 'NWH.AX', 'NWL.AX', 'NWS.AX', 'NXT.AX', 'OFX.AX', 'OGC.AX', 'OML.AX', 'ORA.AX', 'ORE.AX', 'ORG.AX', 'ORI.AX', 'OSH.AX', 'OZL.AX', 'PGH.AX', 'PME.AX', 'PMV.AX', 'PPT.AX', 'PRN.AX', 'PRU.AX', 'PTM.AX', 'QAN.AX', 'QBE.AX', 'QUB.AX', 'REA.AX', 'REG.AX', 'RFF.AX', 'RHC.AX', 'RIO.AX', 'RMD.AX', 'RRL.AX', 'RSG.AX', 'RWC.AX', 'S32.AX', 'SAR.AX', 'SBM.AX', 'SCG.AX', 'SCP.AX', 'SDF.AX', 'SEK.AX', 'SFR.AX', 'SGF.AX', 'SGM.AX', 'SGP.AX', 'SGR.AX', 'SHL.AX', 'SHV.AX', 'SIQ.AX', 'SKC.AX', 'SKI.AX', 'SLF.AX', 'SOL.AX', 'SPK.AX', 'SSM.AX', 'STO.AX', 'STW.AX', 'SUL.AX', 'SUN.AX', 'SVW.AX', 'SYD.AX', 'TAH.AX', 'TCL.AX', 'TGR.AX', 'TLS.AX', 'TNE.AX', 'TPG.AX', 'TRS.AX', 'TWE.AX', 'URW.AX', 'UWL.AX', 'VCX.AX', 'VEA.AX', 'VOC.AX', 'VRL.AX', 'VRT.AX', 'WBC.AX', 'WEB.AX', 'WES.AX', 'WGX.AX', 'WHC.AX', 'WOR.AX', 'WOW.AX', 'WPL.AX', 'WPR.AX', 'WSA.AX', 'WTC.AX', 'XRO.AX']
    # watchlist = {
    #     'OCL.AX': 4.72,
    #     'TNE.AX': 4.41, 
    #     'CGL.AX': 3.54, 
    #     'BVS.AX', 
    #     'XRF.AX', 
    #     'PME.AX', 
    #     'CL1.AX', 
    #     'PPS.AX', 
    #     'EOS.AX', 
    #     'EOF.AX', 
    #     'EML.AX', 
    #     'HUB.AX', 
    #     'APX.AX', 
    #     'WTC.AX', 
    #     'BOT.AX', 
    #     'MVP.AX', 
    #     'ALU.AX', 
    #     'NAN.AX', 
    #     'PCK.AX', 
    #     'CUV.AX', 
    #     'IRE.AX', 
    #     'ZNO.AX', 
    #     'PNV.AX', 
    #     'TLX.AX', 
    #     'RAP.AX', 
    #     'SPL.AX', 
    #     'TTB.AX', 
    #     'GSS.AX', 
    #     'NEA.AX', 
    #     'SKF.AX', 
    #     'MSB.AX', 
    #     'APT.AX', 
    #     'FLC.AX', 
    #     'IPD.AX', 
    #     'PBH.AX', 
    #     'PPH.AX', 
    #     'KZA.AX', 
    #     'WSP.AX', 
    #     'AVH.AX', 
    #     'PAR.AX', 
    #     'OCC.AX', 
    #     'IMU.AX', 
    #     'Z1P.AX',
    #     'TYR.AX', 
    #     'THC.AX', 
    #     'CYP.AX', 
    #     'LVT.AX', 
    #     'ANO.AX', 
    #     'PTX.AX', 
    #     'DW8.AX', 
    #     'BIT.AX', 
    #     'SWF.AX', 
    #     'BRN.AX', 
    #     'RAC.AX', 
    #     'AR9.AX', 
    #     'NUH.AX', 
    #     'RCE.AX', 
    #     'HWH.AX', 
    #     'ANP.AX', 
    #     'PAA.AX', 
    #     'IMC.AX', 
    #     'OSX.AX', 
    #     'PIQ.AX', 
    #     'IBX.AX', 
    #     'DXB.AX', 
    #     'VR1.AX'



    # }
    toPurchase = []
    holdings = []

    valueDict = dict()

    biggestGain = 0
    biggestLoss = 0
    winners = 0
    losers = 0
    daysPassed = 0
    daysInMarket = 0

    #Instance Variables
    def __init__(self):
        self.buyCount = 0
        self.sellCount = 0

    def run(self):
    
        stratBuilder = StrategyBuilder()
        #Retrieve stock data
        tickers = self.getStocks()

        i = 14 #Start at 14 to retrieve indicator data
        j = 0
        #Loop through each day
        while i < tickers[0].closeList.size:
            self.runningDate = tickers[0].closeList.axes[0].date[i]
            self.daysPassed += 1
            if len(self.holdings) > 0:
                self.daysInMarket += 1

            # Logging value for charting
            value = self.capital
            for holding in self.holdings:
                value += holding.units * holding.stock.closeList[i]
            self.valueDict[self.runningDate] = value

            for stock in tickers:
                
                if i < stock.closeList.size:

                    stock.setCurrentPrice(stock.closeList[i])
                    if self.STOP_LOSS > 0:
                        # Sell if hit stop loss
                        for holding in self.holdings:
                            if holding.stock.code == stock.code:
                                if holding.trailingStop == 0:
                                    holding.setTrailingStop(holding.boughtAt * (1-self.STOP_LOSS))
                                elif holding.trailingStop < holding.stock.currentPrice * (1-self.STOP_LOSS):
                                    holding.setTrailingStop(holding.stock.currentPrice * (1-self.STOP_LOSS))
                                    
                                if holding.stock.currentPrice <= holding.trailingStop:
                                    print('Hit stop loss for', stock.code)
                                    self.sellAsStop(holding)

                    #Get Buy/Sell result from Strategy
                    stratResult = stratBuilder.Strategy1(stock, i)
                    
                    if stratResult == 'Buy':
                        print(self.runningDate, 'Buy', stock.code)
                        self.buy(stock, stock.closeList[i], 1) #if self.RUN_DAILY else self.toPurchase.append(stock)
                    elif stratResult == 'Buy2':
                        self.buy(stock, stock.closeList[i], 0.5)
                    elif (stratResult == 'Sell') & (self.haveHolding(stock)): #& (self.toPurchase.__contains__(stock)):
                        # self.toPurchase.remove(stock)

                        self.sell(stock, stock.closeList[i], 1)
                    elif  (stratResult == 'Sell2') & (self.haveHolding(stock)):
                        self.sell(stock, stock.closeList[i], 0.5)

                    # elif (stratResult == 'Sell') & (self.RUN_DAILY):
                    #     #Sell stock if greater than what was bought at
                    #     toSell = []
                    #     for holding in self.holdings:
                    #         if (holding.stock.code == stock.code) & (stock.dailyCloseList[i] > holding.boughtAt):
                    #             toSell.append(holding)
                    #     if len(toSell) > 0: self.sell(toSell, stock.dailyCloseList[i])

                    # #If cleared to purchase go through intraday indicators
                    # if not self.RUN_DAILY:
                    #     if self.toPurchase.__contains__(stock):
                    #         intraday = stock.closeList.axes[0].date[j] #Intraday date

                    #         while (intraday < self.runningDate) & (j < stock.closeList.axes[0].date.size):
                    #             #Move date forward if needing to
                    #             intraday = stock.closeList.axes[0].date[j]
                    #             j+=1

                    #         #Get Buy/Sell indicator for each interval intraday
                    #         while (intraday == self.runningDate) & (j < stock.closeList.axes[0].date.size):
                    #             stock.setCurrentPrice(stock.closeList[j])
                    #             intraday = stock.closeList.axes[0].date[j]

                    #             stratResult = stratBuilder.Strategy1(stock, j, '30m')

                    #             if stratResult == 'Buy':
                    #                 self.buy(stock, stock.closeList[j])
                    #             elif (stratResult == 'Sell') & (self.haveHolding(stock)):
                    #                 toSell = []
                    #                 for holding in self.holdings:
                    #                     if holding.stock.code == stock.code:
                    #                         if stock.closeList[j] > holding.boughtAt:
                    #                             toSell.append(holding)
                    #                 if len(toSell) > 0: self.sell(toSell, stock.closeList[j])

                    #             j+=1
                    #         j = 0
            i+=1

        print('Buys: ', self.buyCount, '\n', 'Sells: ', self.sellCount)
        print('Capital:', self.capital)

        value = self.capital
        for holding in self.holdings:
            value += holding.units * holding.stock.currentPrice

        print('Value: ', value)
        print('Profit:', self.profit)
        print('Winners:', self.winners / self.buyCount)
        print('Losers:', self.losers / self.buyCount)
        print('Biggest Gain:', self.biggestGain)
        print('Biggest Loss', self.biggestLoss)
        print('Time in Market:', self.daysInMarket / self.daysPassed)

        self.writeCSV()

    def getStocks(self):
        print('Retrieving Data...')
        stocks = []
        dailyData = yf.download(
            tickers=self.watchlist,
            # start='2018-01-01',
            # end='2018-12-30',
            period='1y',
            interval='1d',
            group_by='ticker'
        )
        if not self.RUN_DAILY:
            intraData = yf.download(
                tickers=self.watchlist,
                start='2020-06-13',
                end='2020-08-11',
                # period='1mo',
                interval='5m',
                group_by='ticker'
            )
                
        for stock in self.watchlist:
            ticker = Stock(stock)
            stocks.append(ticker)
            #Get daily data
            ticker.setData(dailyData[stock], '1d') if len(self.watchlist) > 1 else ticker.setData(dailyData, '1d')
            ticker.defineIndicators('1d')

            if not self.RUN_DAILY:
                #Get intraday data
                ticker.setData(intraData[stock], '30m') if len(self.watchlist) > 1 else ticker.setData(intraData, '1d')
                ticker.defineIndicators('30m')
        
        return stocks

    def buy(self, stock, price, allocation):
        posSize = self.positionSize(allocation)
        if posSize > 0:
            
            units = int(posSize / price)
            self.holdings.append(Holding(stock, units, price))
            self.capital -= (price * units)
            self.capital -= self.FEES
            self.buyCount += 1

            print(self.runningDate,': Bought', units, 'units of', stock.code, 'at', price, '|', self.capital)


    def sell(self, stock, price, allocation):
        units = 0

        #Sell all held stocks
        for holding in self.holdings:
            if (holding.stock.code == stock.code) & (price > holding.boughtAt):
                posSize = int(holding.units * allocation)
                units += posSize

                diff = posSize * price - posSize * holding.boughtAt

                self.capital += posSize * price
                self.profit += posSize * price - posSize * holding.boughtAt
                holding.setUnits(holding.units - posSize)

                # Remove from holdings if selling all units
                if holding.units == 0:
                    self.holdings.remove(holding)

                if diff > 0:
                    self.winners += 1
                    if self.biggestGain < diff:
                        self.biggestGain = diff
                else:
                    self.losers += 1
                    if self.biggestLoss > diff:
                        self.biggestLoss = diff

        if units > 0:
            self.capital -= self.FEES
            self.profit -= self.FEES
            self.sellCount += 1
            print(self.runningDate,': Sold', units, 'units of', stock.code, 'at', price, '|', self.capital)


    def sellAsStop(self, holding):
        diff = holding.units * holding.stock.currentPrice - holding.units * holding.boughtAt

        self.capital += holding.units * holding.stock.currentPrice
        self.profit += holding.units * holding.stock.currentPrice - holding.units * holding.boughtAt
        self.holdings.remove(holding)
        self.capital -= self.FEES
        self.profit -= self.FEES
        self.sellCount += 1
        print(self.runningDate,': Sold', holding.units, 'units of', holding.stock.code, 'at', holding.stock.currentPrice, '|', self.capital)

        if diff > 0:
                self.winners += 1
                if self.biggestGain < diff:
                    self.biggestGain = diff
        else:
            self.losers += 1
            if self.biggestLoss > diff:
                self.biggestLoss = diff

    def positionSize(self, allocation):
        equity = self.capital + self.profit
        positionSize = equity * self.risk * allocation

        # Have funds available
        if self.capital > self.minPos * allocation:
            if positionSize < self.minPos:
                return self.minPos * allocation - self.FEES
            elif positionSize > self.capital:
                return self.capital - self.FEES
            else: 
                return positionSize - self.FEES
        else:
            return 0

    def haveHolding(self, stock):
        for holding in self.holdings:
            if holding.stock == stock:
                return True
        
        return False

    def lowestHolding(self):
        lowest = self.holdings[0]
        for holding in self.holdings:
            if holding.stock.currentPrice * holding.units < lowest.stock.currentPrice * lowest.units:
                lowest = holding

        return lowest

    def writeCSV(self):

        with open('value.csv', 'w') as f:
            for key in self.valueDict.keys():
                f.write("%s,%s\n"%(key, self.valueDict[key]))