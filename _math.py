import datetime
import pytz
import scipy
import numpy as np
import math

def calcLogR(data, delta=1):
	"""
	Calculates the log return of stock data over given time period.

	The return is calculated over delta, where default delta = 1 weeks.
	Data must be in format: dateTime, OHCLV.
	Gaps in data for weekends and holidays (when NASDAQ is not in session)
	are ignored when calculating the log returns. For example, this means
	that in the calculations, Friday immediately precedes Monday, without
	any gaps for Saturday or Sunday in-between.

	This differs from the previous function, in that the delta is calculated
	through the data without respect to the actual dates of the data. For
	example, this means that for delta=1d, then the log return is calculated
	from the prior value in the list, NOT necessarily from the prior day, as
	weekends and holidays are skipped.
	"""
	EST = pytz.timezone("America/New_York")
	logReturns = []
	for i in range(delta, len(data)):
		now = data[i]
		prior = data[i-delta]

		#dt
		dt = now[0]

		#calc log return as float:
		logO = math.log10(now[1]/prior[1])
		logH = math.log10(now[2]/prior[2])
		logL = math.log10(now[3]/prior[3])
		logC = math.log10(now[4]/prior[4])
		logV = math.log10(now[5]/prior[5]) if now[5] >= 0 and prior[5] >= 0 else -1.0

		print("log return open: "+str(logO)+", mapped to date: "+str(now[0]))

		logReturns.append((dt.replace(tzinfo=EST), logO, logH, logL, logC, logV))

	return logReturns



def ave(data):
	aves = []
	sum = data[0][1]
	num = 1
	for i in range(1, len(data)):
		dt = data[i][0]
		lastDt = data[i-1][0]
		if dt.year == lastDt.year and dt.month == lastDt.month and dt.day == lastDt.day:
			if data[i][1] != 0:
				sum += data[i][1]
				num += 1
		else:
			mean = sum / num
			aves.append([lastDt, mean])
			sum = data[i][1]
			num = 1
	#for the final one not counted
	mean = sum / num
	aves.append([data[len(data)-1][0], mean])

	return aves



def calcSum(data):
	sums = []
	num = 1
	for i in range(1, len(data)):
		dt = data[i][0]
		lastDt = data[i-1][0]
		if dt.year == lastDt.year and dt.month == lastDt.month and dt.day == lastDt.day:
			num += 1
		else:
			sums.append([lastDt, num])
			num = 1
	#for the final one not counted
	sums.append([data[len(data)-1][0], num])

	return sums


def ave2(startDt, endDt, data, zeros=True):
	aves = []
	days = _dayIter(startDt, endDt, datetime.timedelta(days=1))
	days = list(days)[1:]
	EST = pytz.timezone("America/New_York")

	for day in days:
		day = day.replace(tzinfo=EST)
		priorDay = day - datetime.timedelta(days=1)
		priorDay = priorDay.replace(tzinfo=EST)
		day = day.replace(hour=16, minute=0)
		priorDay = priorDay.replace(hour=16, minute=0)
		sum = 0.0
		num = 0
		for line in data:
			dt = line[0]
			if dt > priorDay and dt <= day:
				#sum += line[1] if line[1] > 0 else 2*line[1] #TEST TO SEE IF WEIGHTING NEGS MAKES MORE ACCURATE
				sum += line[1]
				num += 1
		mean = sum / float(num) if num != 0 else 0
		aves.append([day, mean])
		sum = 0.0
		num = 0

	if not zeros:
		i = 0
		while True:
			if i == len(aves):
				break
			elif -0.0005 < aves[i][1] < 0.0005:
				aves.pop(i)
				i -= 1
			i += 1


	return aves




def calcSum2(startDt, endDt, data):
	sums = []
	days = _dayIter(startDt, endDt, datetime.timedelta(days=1))
	days = days[1:]
	for day in days:
		priorDay = day - datetime.timedelta(days=1)
		day.replace(hour=16, minute=0)
		priorDay.replace(hour=16, minute=0)
		num = 0
		for line in data:
			dt = line[0]
			if dt > priorDay and dt <= day:
				num += 1
		sums.append([day.date, num])
		num = 0

	return sums




def calcLSRL(x, y):
	"""Calculates LSRL (a.k.a. OLS) in form: a + bx."""

	#required for calcs below:
	meanx = np.mean(x)
	meany = np.mean(y)
	
	#n & df
	n = len(x)
	df = n-2

	#LSRL in form: a + bx
	b_numerator = sum([(x[i] - meanx)*(y[i] - meany) for i in range(n)])
	b_denominator = sum([(x[i] - meanx)**2 for i in range(n)])
	b = b_numerator/b_denominator

	a = meany - b*meanx

	#R^2
	SSres = sum([(y[i] - (a + b*x[i]))**2 for i in range(n)])
	SStot = sum([(y[i] - meany)**2 for i in range(n)])

	Rsqr = 1 - (SSres/SStot)

	#R
	R = math.sqrt(Rsqr)

	#Standard error.
	se_numerator = math.sqrt(SSres / (n-2))
	se_denominator = math.sqrt(b_denominator)

	se = se_numerator/se_denominator

	#t score.
	t = b/se

	

	return a, b, n, df, Rsqr, R, se, t


def calcResids(x, y, LSRL):
	a, b, n, df, Rsqr, R, se, t = LSRL
	data = zip(x, y)
	resids = []

	for point in data:
		xi = point[0]
		yi = point[1]
		yhat = a + b*xi
		resid = yi - yhat
		resids.append(resid)

	return resids



def confInter(LSRL, alpha=0.05):
	a, b, n, df, Rsqr, R, se, t = LSRL
	critical = 1.96
	me = critical*se
	low = b - me
	high = b + me

	return (low, high)


def cov(x, y):
	"""Returns covariance, which is equal to: E[xy] - E[x]E[y]."""
	#where E[] is the expected value, a.k.a. the mean.
	product = []
	for i in range(len(x)):
		product.append(x[i]*y[i])

	meanp = np.mean(product)
	meanx = np.mean(x)
	meany = np.mean(y)

	cov = meanp - meanx*meany
	return cov



def R(x, y):
	"""
	Returns Pearson's correlation coeff between x and y.

	This is equal to cov(x,y)/sqrt(var(x)var(y)).
	"""
	covar = cov(x, y)
	varX = np.var(x)
	varY = np.var(y)
	Rcoeff = covar / math.sqrt(varX*varY)
	return Rcoeff



def laggedRFunc(tsY, tsX, maxLag):
	"""
	Calculates and returns the correlation between the X time series
	and Y time series, up to and including max lag.

	Returns list of R's, in pairs of (lag, R).
	The lag is performed on the tsX series, to determine if lagged values
	of the tsX series have effect upon the tsY series.
	"""
	coeffs = []

	#lag=0 (i.e. R=1)
	Rcoeff = R(tsY, tsX)
	coeffs.append([0, Rcoeff])

	#other lags
	for lag in range(1, maxLag+1):
		ts = tsY[lag:]
		lagts = tsX[:-lag]
		Rcoeff = R(ts, lagts)
		coeffs.append([lag, Rcoeff])
	return coeffs


def ljungBox(x, y, maxLag):
	if len(x) != len(y): return []
	coeffs = laggedRFunc(y, x, maxLag)
	n = len(x)

	coeffs[0].append("none")
	coeffs[0].append("none")

	for lag in range(1, maxLag+1):
		frac = 0.0
		for k in range(1, lag+1):
			frac += (coeffs[k][1]**2 / (n-k))
		Q = frac*n*(n+2)
		pval = scipy.stats.chi2.sf(Q, lag)
		coeffs[lag].append(Q)
		coeffs[lag].append(pval)

	return coeffs


def pair(logR, exog, rsent, trend, lag=0):
	"""
	Pairs together the log return data and number of article data based on date.
	"""
	pairs = []

	for lr in logR:
		lDt = lr[0].date()
		for e in exog:
			eDt = e[0].date()-datetime.timedelta(days=lag)
			if lDt == eDt:
				o = lr[1]
				h = lr[2]
				l = lr[3]
				c = lr[4]
				v = lr[5]
				ex = e[1]
				pairs.append([lDt, o, h, l, c, v, ex])
				break
	for p in pairs:
		pDt = p[0]
		for r in rsent:
			rDt = r[0].date()-datetime.timedelta(days=lag)
			if pDt == rDt:
				p.append(r[1])
				break
	for p in pairs:
		pDt = p[0]
		for t in trend:
			tDt = t[0].date()-datetime.timedelta(days=lag)
			if pDt == tDt:
				p.append(t[1])
				break

	return pairs


def weightRank(articles, rankWeights):
	lastDate = datetime.date.today()

	for a in articles:
		date = a[0].date
		if date != lastDate:
			num = 0
			print a[2]	#or [4], depending on the sent scheme
			wr = a[2] * rankWeights[num]
			a.append(wr)
			lastDate = date
		else:
			num += 1
			num = 5 if num > 5 else num
			wr = a[2] * rankWeights[num]
			a.append(wr)
			lastDate = date

	return articles



def diff(data, numDiff=1):
	"""
	Differences time series ts numDiff number of times.

	If numDiff > 1, then performs difference between each
	two consecutive points numDiff times. The difference is
	assigned to the datetime of the latter of each consecutive
	pair of points.
	dt is the corresponding datetimes for this series (x)
	ts is the time series values (y)
	"""

	dt, ts = zip(*data)

	for x in range(numDiff):

		new_dt = dt[1:]
		new_ts = []

		for i in range(1, len(ts)):
			d = ts[i] - ts[i-1]
			new_ts.append(d)

		dt = new_dt
		ts = new_ts

	diff_data = zip(dt, ts)

	for i in range(len(diff_data)):
		diff_data[i] = list(diff_data[i])

	return diff_data


def discrete(x, y):
	"""
	Quantizes the standard LSRL procedure to pos and neg.
	"""
	#x>0 y>0
	xPosYPos = 0
	xPosYNeg = 0
	xNegYPos = 0
	xNegYNeg = 0
	for i in range(len(x)):
		if x[i] > 0 and y[i] > 0:
			xPosYPos += 1
		elif x[i] > 0 and y[i] < 0:
			xPosYNeg += 1
		elif x[i] < 0 and y[i] > 0:
			xNegYPos += 1
		elif x[i] < 0 and y[i] < 0:
			xNegYNeg += 1

	#prob of getting y=pos given that x=pos
	yPosGivenXPos = xPosYPos / float(xPosYPos+xPosYNeg) if float(xPosYPos+xPosYNeg) > 0 else 0
	#prob of getting y=neg given that x=neg
	yNegGivenXNeg = xNegYNeg / float(xNegYNeg+xNegYPos) if float(xNegYNeg+xNegYPos) > 0 else 0
	#prob of getting y=neg given that x=neg
	yPosGivenXNeg = xNegYPos / float(xNegYNeg+xNegYPos) if float(xNegYNeg+xNegYPos) > 0 else 0
	#prob of getting y=neg given that x=neg
	yNegGivenXPos = xPosYNeg / float(xPosYNeg+xPosYPos) if float(xPosYNeg+xPosYPos) > 0 else 0

	print("Probability of y>0 given x>0: "+str(yPosGivenXPos))
	print("Probability of y<0 given x<0: "+str(yNegGivenXNeg))
	print("")
	print("Probability of y<0 given x>0: "+str(yNegGivenXPos))
	print("Probability of y>0 given x<0: "+str(yPosGivenXNeg))




def _dayIter(start, end, delta):
	"""
	Returns datetimes from [start, end) for use in iteration.
	"""
	current = start
	while current < end:
		yield current
		current += delta



def ma(data, period=20):
	"""
	Calculates the moving average of the timeseries ts.
	"""
	dt, ts = zip(*data)
	new_dt = []
	new_ts = []

	for i in range(period, len(ts)):
		sum = 0
		for j in range(i-period, i):
			sum += ts[j]
		ave = sum/period

		new_dt.append(dt[i])
		new_ts.append(ave)

	new_data = [new_dt, new_ts]
	new_data = zip(*new_data)

	return new_data



def median(data, period=20):
	"""
	Calculates the moving average of the timeseries ts.
	"""
	dt, ts = zip(*data)
	new_dt = []
	new_ts = []

	for i in range(period, len(ts)):
		sub = []
		for j in range(i-period, i):
			sub.append(ts[j])
		med = np.median(sub)

		new_dt.append(dt[i])
		new_ts.append(med)

	new_data = [new_dt, new_ts]
	new_data = zip(*new_data)

	return new_data


def onlyLargeReturns(data, pd=5):
	final = []
	for i in range(pd, len(data)):
		past = data[i-pd:i]
		dt, o, h, l, c, v = zip(*past)
		m = np.mean(c)
		s = np.std(c)
		if abs(data[i][4] - m) >= s:
			final.append(data[i])
	return final