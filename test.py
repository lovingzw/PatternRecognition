import datetime
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
import copy
import tushare as ts
from dtw import fastdtw
from arc import arc_circle_gen
from sma import moving_average
from simpleplot import arc_plot

STARTDATE = '2018-05-01'
ENDDATE = '2018-06-31'
STOCKCODE = '300682'
WINDOWSIZE = 5
TIMESPAN_MIN = 21
TIMESPAN_MAX = 40





if __name__ == '__main__':
    klineData = ts.get_k_data(STOCKCODE, start=STARTDATE, end=ENDDATE)
    smoothedData = moving_average(klineData, WINDOWSIZE, 'close')
    TOTALDATES = len(smoothedData)

    endDate = TIMESPAN_MIN - 1
    startDate = endDate - TIMESPAN_MIN + 1
    leftBound = 0

    while endDate < TOTALDATES :
        curPeriod = copy.deepcopy(smoothedData[endDate-TIMESPAN_MIN : endDate])

        notMatch = True
        dateInc = 1

        leftBound = max(leftBound, endDate-TIMESPAN_MAX+1)
        startDate = endDate - TIMESPAN_MIN + 1
        while startDate >= leftBound :
            #do the match job here
            #if match
                #leftBound = endDate + 1
                #dateInc = TIMESPAN_MIN
                #save the arc

            startDate = startDate - 1

        endDate = endDate + dateInc






