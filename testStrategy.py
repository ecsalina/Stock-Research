import datetime
import pytz
import pandas as pd
import numpy as np
from _inputoutput import *
import _plotter


#Test Methods:
def daily(stock, exog, ma, port, trans, transOccured, dt):
	if transOccured:
		port = close(stock, 200, trans[-1][1], port)
		print("Portfolio: "+str(port))
	if exog > ma:
		port = open(stock, 200, port, trans, dt)	#long
		print("LONG")
	if exog <= ma:
		port = open(stock, -200, port, trans, dt)	#short
		print("SHORT")
	print("Portfolio: "+str(port))
	return port

def dailyRand(stock, port, trans, transOccured, dt):
	if transOccured:
		port = close(stock, 200, trans[-1][1], port)
		print("Portfolio: "+str(port))
	rand = np.random.randn()
	if rand > 0:
		port = open(stock, 200, port, trans, dt)	#long
		print("LONG")
	if rand <= 0:
		port = open(stock, -200, port, trans, dt)	#short
		print("SHORT")
	print("Portfolio: "+str(port))
	return port

def final(stock, port, transactions, transOccured):
	if transOccured:
		port = close(stock, 200, transactions[-1][1], port)
	return port

def open(stock, amount, port, transactions, dt):
	value = stock*amount
	port -= value
	transactions.append((dt, value))
	return port

def close(stock, amount, transaction, port):
	action = -1 if transaction > 0 else 1
	value = action*stock*amount
	port -= value
	return port



#Actual Logic:
startDt = datetime.datetime(day=1, month=10, year=2014)
endDt = datetime.datetime(day=1, month=4, year=2015)
#cid = 14135				#GE
#cid = 99624			#CSCO
#cid = 660463			#AMZN
cid = 304466804484872	#GOOG

stocks = collectStockData(cid, startDt, endDt, "stockData.csv")
#write("stockData.csv", stocks)
dt, o, h, l, c, v = zip(*stocks)
stocks = pd.Series(c, index=dt)
stocksIndex = pd.to_datetime(stocks.index)
stocksIndex = stocksIndex.map(lambda t: t.replace(hour=16))
stocks.index = stocksIndex

exog = pd.read_csv("strategy.csv", delimiter=",", index_col="datetime", header=0)
exogIndex = pd.to_datetime(exog.index)
exog.index = exogIndex
exog = exog["value"]

ma = pd.rolling_mean(exog, 10)

bothIndex = stocks.index.intersection(exog.index)
threeIndex = bothIndex.intersection(ma.index)
stocks = stocks.reindex(threeIndex)
exog = exog.reindex(threeIndex)
ma = ma.reindex(threeIndex)

lag = 1
preLagIndex = threeIndex
postLagIndex = threeIndex[lag:]

stocks = stocks.reindex(preLagIndex)
exog = exog.reindex(postLagIndex)
ma = ma.reindex(postLagIndex)


#Analysis
portfolio = 100000.00	#$100 thousand
transactions = []
prevLen = 0
transOccured = False

for i, index in enumerate(preLagIndex):
	if index == preLagIndex[-1] or i < 10:
		continue
	s = stocks[i]
	e = exog[i]
	m = ma[i]
	print("close price: "+str(s)+", trend: "+str(e)+", moving average: "+str(m))
	portfolio = daily(s, e, m, portfolio, transactions, transOccured, index)
	#portfolio = dailyRand(s, portfolio, transactions, transOccured, index)
	print("\n")
	if len(transactions) != prevLen:
		transOccured = True
		prevLen = len(transactions)
	else:
		transOccured = False

portfolio = final(stocks[-1], portfolio, transactions, transOccured)
print("Total cash remaining in portfolio: "+str(portfolio))



#Plot
dt, t = zip(*transactions)
transactions = pd.Series(t, index=dt)
_plotter.strategy("GOOG", stocks, exog, ma, transactions, 200)