import getpass
import scipy
import os
import datetime
import pytz
import math
import tabulate
from matplotlib import pyplot as plt
import statsmodels.api as sm
import numpy as np
import gtrends
from _inputoutput import *
import _math
import _plotter


#cid = 304466804484872	#GOOG
#cid = 22144			#AAPL
#cid = 12607212			#TSLA
#cid = 660463			#AMZN
#cid = 663876			#XOM
#cid = 358464			#MSFT
#cid = 697410			#DJIA -- technically this is the SPDR ETF, but it follows the same trend as the DJIA, and I cannot export the DJIA as csv with Google.
#cid = 13772865			#S&P 500 -- technically is VOO ETF
cid = 14135				#GE
#cid = 99624			#CSCO
#cid = 38230			#WMT
#cid = 1033				#AXP
#cid = 6550				#KO

EST = pytz.timezone("America/New_York")

articlePath = "rawArticleData.csv"
artSentPath = "rawArticleData.xlsx"
stockPath = "rawStockData.csv"
trendPath = "rawTrendData.csv"
terms = ["GE"]

startDt = datetime.datetime(day=1, month=10, year=2014)
endDt = datetime.datetime(day=1, month=7, year=2015)

#load stuff up
print("collecting data from "+str(startDt)+" til "+str(endDt))

stocks = collectStockData(cid, startDt, endDt, stockPath)

if os.path.isfile(trendPath):
	trends = read(trendPath)
else:
	username = raw_input("username: ")
	password = getpass.getpass("password: ")
	trends = gtrends.collectTrends(username, password, terms, startDt, endDt, granularity='d')
	trends = trends[1:]
	write(trendPath, trends)

#if os.path.isfile(articlePath):
#	articles = readRaw(articlePath)
#else:
#	articles = collectArticles(terms, startDt, endDt)
#	write(articlePath, articles)
#raw_input("Waiting for Semantria. Press enter when ready to continue.")

articles = getAllArtData(artSentPath, entSent=True)

cats = ["Analyst Recommendation", "Legal", "Deals", "Product", "Stocks",
		"Partnership", "Employment"]



#ALL CATEGORIES (i.e. categories not taken into account)
#Organization of article data --> [dt, site, url, text, sent, [ents], [entSents], [themes], [wikiCats], [userCats]]
trimArticles = []
for trend in trends:
	tdt = trend[0]
	for art in articles:
		adt = art[0]
		if (tdt-datetime.timedelta(days=1)).replace(hour=16, minute=30, tzinfo=EST) < adt <= tdt.replace(hour=16, minute=30, tzinfo=EST):
			if art[4] < -0.05 or 0.22 < art[4]:
				#weightedVal = math.copysign(trend[1], art[4])
				weightedVal = trend[1]*art[4]
				weightedVal = weightedVal*3 if weightedVal<0 else weightedVal
				art.append(weightedVal)
				trimArticles.append(art)

logR = _math.calcLogR(stocks, delta=1)
adt, source, url, text, sent, ent, entsent, theme, cat, ucat, weight = zip(*trimArticles)
exog = _math.ave2(startDt, endDt, zip(adt, weight), zeros=True)
rawSent = _math.ave2(startDt, endDt, zip(adt, sent))
pairedData = _math.pair(logR, exog, rawSent, trends, lag=0)
dt, o, h, l, R, v, e, rsent, t = zip(*pairedData)
absR = [abs(r) for r in R]

Rvabsr = scipy.stats.linregress(v, absR)[2]
Rvr = scipy.stats.linregress(v, R)[2]
Rtabsr = scipy.stats.linregress(t, absR)[2]
Rtr = scipy.stats.linregress(t, R)[2]

Rtv = scipy.stats.linregress(t, v)[2]

Rrsentr = scipy.stats.linregress(rsent, R)[2]
RerAllCat = scipy.stats.linregress(e, R)[2]

Rte = scipy.stats.linregress(t, e)[2]

#Header:
print(terms[0])

#Data Summary:
print("-------ALL CATEGORIES--------")
header = ["type", "R value"]
data = [
		["v vs absR",Rvabsr],
		["v vs R",Rvr],
		["t vs absR",Rtabsr],
		["t vs R",Rtr],
		["t vs v",Rtv],
		["rsent vs R",Rrsentr],
		["e (all cat) vs R",RerAllCat],
		["t vs e (all cat)",Rte]
]
print("\n")
print("*********Linear Regression**********")
print(tabulate.tabulate(data, headers=header))

#William's modification on the Hotelling t statistic:
Ryx1 = RerAllCat
Ryx2 = Rtr
Rx1x2 = Rte
n = len(R)
tNum = (Ryx1 - Ryx2) * math.sqrt((n - 3)*(1 + Rx1x2))
fracNum = (Ryx1 - Ryx2)**2 * (1-Rx1x2)**3
Rdet = 1 - Ryx1**2 - Ryx2**2 - Rx1x2**2 + (2*Ryx1*Ryx2*Rx1x2)
tDen = math.sqrt(2*Rdet + fracNum/(4*(n-1)))

tval = tNum/tDen
df = len(R)-3
pval = scipy.stats.t.sf(tval, df)
header = ["type", "value"]
data = [
		["tval",tval],
		["pval",pval],
		["df",df]
]
print("\n")
print("*William's Modified Hotelling T Test*")
print(tabulate.tabulate(data, headers=header))

#Ljung Box Test & Autocorrelation/Crosscorrelation
coeffs = _math.ljungBox(R, R, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("\n")
print("*Ljung-Box Test for Crosscorrelation*")
print("## R vs R ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(t, t, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## t vs t ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(rsent, rsent, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## rsent vs rsent ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(e, e, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## e vs e ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(e, R, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## e vs R ##")
print(tabulate.tabulate(data, headers=header))











#SPECIFIC CATEGORIES (i.e. only those with actual categories labelled)
catIndex = []
for i,art in enumerate(trimArticles):
	if len(set(art[9]) & set(cats)) > 0:
		catIndex.append(i)
catArts = []
for i in catIndex:
	catArts.append(trimArticles[i])
adt, source, url, text, sent, ent, entsent, theme, cat, ucat, weight = zip(*catArts)
exog = _math.ave2(startDt, endDt, zip(adt, weight), zeros=True)
rawSent = _math.ave2(startDt, endDt, zip(adt, sent))
pairedData = _math.pair(logR, exog, rawSent, trends, lag=0)
dt, o, h, l, R, v, e, rsent, t = zip(*pairedData)
absR = [abs(r) for r in R]

Rvabsr = scipy.stats.linregress(v, absR)[2]
Rvr = scipy.stats.linregress(v, R)[2]
Rtabsr = scipy.stats.linregress(t, absR)[2]
Rtr = scipy.stats.linregress(t, R)[2]

Rtv = scipy.stats.linregress(t, v)[2]

Rrsentr = scipy.stats.linregress(rsent, R)[2]
RerSpecCat = scipy.stats.linregress(e, R)[2]

Rte = scipy.stats.linregress(t, e)[2]

#Data Summary:
print("\n\n")
print("--------SPECIFIC CATEGORIES--------")
header = ["type", "R value"]
data = [
		["v vs absR",Rvabsr],
		["v vs R",Rvr],
		["t vs absR",Rtabsr],
		["t vs R",Rtr],
		["t vs v",Rtv],
		["rsent vs R",Rrsentr],
		["e (spec cat) vs R",RerSpecCat],
		["t vs e (spec cat)",Rte]
]
print("\n")
print("*********Linear Regression*********")
print(tabulate.tabulate(data, headers=header))

#William's modification on the Hotelling t statistic:
Ryx1 = RerSpecCat
Ryx2 = Rtr
Rx1x2 = Rte
n = len(R)
tNum = (Ryx1 - Ryx2) * math.sqrt((n - 3)*(1 + Rx1x2))
fracNum = (Ryx1 - Ryx2)**2 * (1-Rx1x2)**3
Rdet = 1 - Ryx1**2 - Ryx2**2 - Rx1x2**2 + (2*Ryx1*Ryx2*Rx1x2)
tDen = math.sqrt(2*Rdet + fracNum/(4*(n-1)))

tval = tNum/tDen
df = len(R)-3
pval = scipy.stats.t.sf(tval, df)
header = ["type", "value"]
data = [
		["tval",tval],
		["pval",pval],
		["df",df]
]
print("\n")
print("*Williams Modified Hotelling T Test*")
print(tabulate.tabulate(data, headers=header))

#Ljung Box Test & Autocorrelation/Crosscorrelation
coeffs = _math.ljungBox(R, R, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("\n")
print("*Ljung-Box Test for Crosscorrelation*")
print("## R vs R ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(t, t, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## t vs t ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(rsent, rsent, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## rsent vs rsent ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(e, e, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## e vs e ##")
print(tabulate.tabulate(data, headers=header))

coeffs = _math.ljungBox(e, R, maxLag=7)
header = ["lag", "R value", "Q", "p value"]
data = coeffs
print("## e vs R ##")
print(tabulate.tabulate(data, headers=header))