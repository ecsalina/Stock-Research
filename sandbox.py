import scipy
import os
import datetime
import pytz
import math
import getpass
import tabulate
from matplotlib import pyplot as plt
import statsmodels.api as sm
import numpy as np
import gtrends
from _inputoutput import *
import _math
import _plotter


cid = 304466804484872	#GOOG
#cid = 22144			#AAPL
#cid = 12607212			#TSLA
#cid = 660463			#AMZN
#cid = 663876			#XOM
#cid = 358464			#MSFT
#cid = 697410			#DJIA -- technically this is the SPDR ETF, but it follows the same trend as the DJIA, and I cannot export the DJIA as csv with Google.
#cid = 13772865			#S&P 500 -- technically is VOO ETF
#cid = 14135			#GE
#cid = 99624				#CSCO
#cid = 38230			#WMT
#cid = 6550				#KO

EST = pytz.timezone("America/New_York")

articlePath = "rawArticleData.csv"
artSentPath = "rawArticleData.xlsx"
stockPath = "rawStockData.csv"
trendPath = "rawTrendData.csv"
terms = ["GOOG"]

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
#names = ["Coca-Cola", "Coke"]



#ALL CATEGORIES (i.e. categories not taken into account)
#Organization of article data --> [dt, site, url, text, sent, [ents], [entSents], [themes], [wikiCats], [userCats]]
trimArticles = []
for trend in trends:
	tdt = trend[0]
	for art in articles:
		adt = art[0]
		if (tdt-datetime.timedelta(days=1)).replace(hour=16, minute=30, tzinfo=EST) < adt <= tdt.replace(hour=16, minute=30, tzinfo=EST):
				if art[4] < -0.05 or 0.22 < art[4]:
					if len(set(art[9]) & set(cats)) > 0:
					#cont = [ent for ent in art[5] if isinstance(ent, basestring) and ("coca-cola" in ent.lower() or "coke" in ent.lower())]
					#if len(cont) > 0:
						#index = art[5].index(cont[0])
						#weightedVal = trend[1]*art[6][index]
						weightedVal = trend[1]*art[4]
						#weightedVal = math.copysign(trend[1], art[4])
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

#pair = zip(t, R)
#pair = [line for line in pair if abs(line[1]) < 0.03]
#t, R = zip(*pair)
#pair = zip(e, R)
#pair = [line for line in pair if abs(line[1]) < 0.03]
#e, R = zip(*pair)

#R = [abs(r) for r in R]

RerAllCat = scipy.stats.linregress(e, R)
print(RerAllCat)
_plotter.xy(terms[0], e, R)

_plotter.xy4sub(terms[0], dt, R, dt, e, dt, rsent, dt, t)

#sum of returns based on exog data
summ = 0.0
for i, ex in enumerate(e):
	if ex > 0:
		summ += R[i]
	else:
		summ -= R[i]
print(str(summ))