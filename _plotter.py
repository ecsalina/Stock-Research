import math
import datetime
from  dateutil.rrule import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.finance as fn
import matplotlib.dates
import matplotlib.collections as mc


def xy(ticker, x, y, LSRL=None):
	fig = plt.figure()

	if LSRL != None:
		a, b, n, df, Rsqr, R, se, t = LSRL
		#form: y = a + bx
		LSRL_x = [-1, 1]
		LSRL_y = []
		y0 = a + b*LSRL_x[0]
		y1 = a + b*LSRL_x[1]
		LSRL_y.append(y0)
		LSRL_y.append(y1)

		plt.plot(x, y, "o", LSRL_x, LSRL_y, "r")
	else:
		#zeroLineX = [-20, 140]
		#zeroLineY = [0, 0]
		plt.plot(x, y, "o")

	#plt.xlim(-10, 140)
	#plt.ylim(-0.1, 0.1)

	#plt.xlim(0, 60)
	#plt.ylim(-1, 1)
	#plt.locator_params(nbins=15)
	#plt.grid()

	#plt.xlim(-0.1, 0.1)
	#plt.ylim(-0.1, 0.1)
	plt.grid()

	plt.xlabel("query volume")
	plt.ylabel("log returns")
	plt.title(ticker+" Query Volume vs  Returns")

	fig.autofmt_xdate()

	plt.show()



def xy2(ticker, x1, y1, x2, y2):
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()

	ax1.plot(x1, y1, color="r")
	ax2.plot(x2, y2, color="b")

	ax1.set_ylim(-0.03, 0.03)
	ax2.set_ylim(-8, 8)

	ax1.set_ylabel("log returns (red)")
	ax2.set_ylabel("weighted sent (blue)")
	plt.title(ticker+" Weighted Sent & Returns")

	fig.autofmt_xdate()
	plt.grid()

	plt.show()



def xy3(ticker, x1, y1, x2, y2, x3, y3, line=None):
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax3 = ax1.twinx()

	ax1.plot(x1, y1, color="r")
	ax2.plot(x2, y2, color="b")
	ax3.plot(x3, y3, color="g")

	#ax1.set_ylim(-0.04, 0.04)
	#ax2.set_ylim(0, 0.45)
	#ax3.set_ylim(-0.45, 0)

	if line != None:
		lineY = []
		for x in x3:
			lineY.append(line)
		ax3.plot(x3, lineY, color="m")

	ax1.set_ylabel("log returns (red)")
	ax2.set_ylabel("weighted sentiment (blue), moving average-10 (green)")
	plt.title(ticker+" Weighted Sentiment & Daily Log Returns")

	fig.autofmt_xdate()

	minor = matplotlib.dates.WeekdayLocator(byweekday=(MO, TU, WE, TH, FR, SA, SU))
	ax1.xaxis.set_minor_locator(minor)
	ax2.xaxis.set_minor_locator(minor)
	ax3.xaxis.set_minor_locator(minor)
	ax1.grid(which="both")
	ax2.grid(which="both")
	ax3.grid(which="both")

	#plt.grid()
	plt.show()


def xy4(ticker, x1, y1, x2, y2, x3, y3, x4, y4):
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax3 = ax1.twinx()

	ax1.plot(x1, y1, color="r")
	ax2.plot(x2, y2, color="b")
	ax3.plot(x3, y3, "g", x4, y4, "m")

	#ax1.set_ylim(-0.04, 0.04)
	#ax2.set_ylim(0, 15)
	#ax3.set_ylim(0, 15)

	ax1.set_ylabel("log returns (red)")
	ax2.set_ylabel("weighted sentiment (blue), moving average-10 (green)")
	plt.title(ticker+" Weighted Sentiment & Daily Log Returns")

	fig.autofmt_xdate()

	minor = matplotlib.dates.WeekdayLocator(byweekday=(MO, TU, WE, TH, FR, SA, SU))
	ax1.xaxis.set_minor_locator(minor)
	ax2.xaxis.set_minor_locator(minor)
	ax3.xaxis.set_minor_locator(minor)
	ax1.grid(which="both")
	ax2.grid(which="both")
	ax3.grid(which="both")

	#plt.grid()
	plt.show()


def strategy(ticker, stock, exog, ma, trans, amt):
	longs = []
	shorts = []
	for day in trans.index.tolist():
		if trans[day] > 0:		#we went LONG
			longs.append((day, abs(trans[day]/amt)))
		elif trans[day] <= 0: 	#we went SHORT
			shorts.append((day, abs(trans[day]/amt)))

	x1 = stock.index.tolist()
	y1 = stock.tolist()
	x2 = exog.index.tolist()
	y2 = exog.tolist()
	x3 = ma.index.tolist()
	y3 = ma.tolist()
	x4, y4 = zip(*longs)
	x5, y5 = zip(*shorts)

	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax3 = ax1.twinx()
	ax4 = ax1.twinx()
	ax5 = ax1.twinx()

	ax1.plot(x1, y1, "r", x4, y4, "g^", x5, y5, "gv")
	ax2.plot(x2, y2, "b", x3, y3, "m")
	#ax3.plot(x3, y3, "p")
	#ax4.plot(x4, y4, "g^")
	#ax5.plot(x5, y5, "gv")

	#ax1.set_ylim(-0.04, 0.04)
	#ax2.set_ylim(0, 15)
	#ax3.set_ylim(0, 15)

	ax1.set_ylabel("log returns (red)")
	ax2.set_ylabel("weighted sentiment (blue), moving average-10 (green)")
	plt.title(ticker+" Query Volume, Returns")

	fig.autofmt_xdate()

	#minor = matplotlib.dates.WeekdayLocator(byweekday=(MO, TU, WE, TH, FR, SA, SU))
	#ax1.xaxis.set_minor_locator(minor)
	#ax2.xaxis.set_minor_locator(minor)
	#ax3.xaxis.set_minor_locator(minor)
	#ax1.grid(which="both")
	#ax2.grid(which="both")
	#ax3.grid(which="both")

	#plt.grid()
	plt.show()


def xy3sub(ticker, x1, y1, x2, y2, x3, y3):
	fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
	ax1.plot(x1, y1, color="r")
	ax2.plot(x2, y2, color="b")
	ax3.plot(x3, y3, color="g")

	#ax1.set_ylim(-0.04, 0.04)
	#ax2.set_ylim(0, 0.45)
	#ax3.set_ylim(-0.45, 0)

	ax1.set_ylabel("log returns (red)")
	ax2.set_ylabel("weighted sentiment (blue)")
	ax3.set_ylabel("moving average-10 (green)")
	plt.title(ticker+" Weighted Sentiment & Daily Log Returns")

	fig.autofmt_xdate()
	plt.show()




def xy4sub(ticker, x1, y1, x2, y2, x3, y3, x4, y4):
	fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
	#return
	ax1.plot(x1, y1, color="r")
	#sent
	ax2.plot(x2, y2, color="c")
	ax2b = ax2.twinx()
	ax2b.plot(x3, y3, color="m")
	#gtrend
	ax3.plot(x4, y4, color="b")

	fig.autofmt_xdate()
	plt.show()