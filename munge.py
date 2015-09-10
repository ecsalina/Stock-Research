import datetime
import pytz
from _inputoutput import *
import _math

trendPath = "rawTrendData.csv"
artSentPath = "rawArticleData.xlsx"
articles = getAllArtData(artSentPath, entSent=True)
trends = read(trendPath)

cats = ["Analyst Recommendation", "Legal", "Deals", "Product", "Stocks",
		"Partnership", "Employment"]


EST = pytz.timezone("America/New_York")
startDt = datetime.datetime(day=1, month=10, year=2014)
endDt = datetime.datetime(day=1, month=7, year=2015)

#ALL CATEGORIES (i.e. categories not taken into account)
#Organization of article data --> [dt, site, url, text, sent, [ents], [entSents], [themes], [wikiCats], [userCats]]
trimArticles = []
for trend in trends:
	tdt = trend[0]
	#counter = 0
	for art in articles:
		adt = art[0]
		if (tdt-datetime.timedelta(days=1)).replace(hour=16, minute=30, tzinfo=EST) < adt <= tdt.replace(hour=16, minute=30, tzinfo=EST):
			#if counter < 5:
				if art[4] < -0.05 or 0.22 < art[4]:
					if len(set(art[9]) & set(cats)) > 0:
						weightedVal = trend[1]*art[4]
						#weightedVal = math.copysign(trend[1], art[4])
						weightedVal = weightedVal*3 if weightedVal<0 else weightedVal
						art.append(weightedVal)
						trimArticles.append(art)
			#			counter += 1
			#else:
			#	break

adt, source, url, text, sent, ent, entsent, theme, cat, ucat, weight = zip(*trimArticles)
exog = _math.ave2(startDt, endDt, zip(adt, weight), zeros=True)

write("strategy.csv", exog)