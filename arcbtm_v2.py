import datetime
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num, num2date
import copy
import tushare as ts
from dtw import fastdtw
from sma import moving_average
from simpleplot import arc_plot
from template import template_gen

STARTDATE = '2018-01-01'
ENDDATE = '2018-06-31'
STOCKCODE = '300682'
WINDOWSIZE = 5
TIMESPAN_MIN = 21
TIMESPAN_MAX = 40
SIM_THRESHOLD = 2
CIRCLE_HORIZONTAL_THRESHOLD = 0.01


if __name__ == '__main__':
    klineData = ts.get_k_data(STOCKCODE, start=STARTDATE, end=ENDDATE)
    smoothedData = moving_average(klineData, WINDOWSIZE, 'close')

    klineData = klineData.iloc[WINDOWSIZE-1:]
    TOTALDATES = len(smoothedData)

    # [startDate, endDate]
    savedPatternList = []
    templateList = []
    for i in range(TIMESPAN_MIN, TIMESPAN_MAX+1):
        templateList.append(template_gen('circle', i, i/2.0, 1))
    pricePatternList = []

    distList = []

    # price pattern lasts from [startDate, endDate]
    endDate = TIMESPAN_MIN - 1
    startDate = endDate - TIMESPAN_MIN + 1
    leftBound = 0

    while endDate < TOTALDATES:
        dateInc = 1
        leftBound = max(leftBound, endDate-TIMESPAN_MAX+1)
        startDate = endDate - TIMESPAN_MIN + 1

        while startDate >= leftBound:
            curPeriod = copy.deepcopy(smoothedData[startDate:endDate+1])
            lenPeriod = endDate - startDate + 1
            curTemplate = templateList[lenPeriod - TIMESPAN_MIN]

            sortedPeriod = copy.deepcopy(curPeriod)
            sortedPeriod = sorted(sortedPeriod, key=lambda sortedPeriod: sortedPeriod[1])
            periodRange = sortedPeriod[lenPeriod-1][1] - sortedPeriod[0][1]
            for i in range(lenPeriod):
                curPeriod[i][1] = (curPeriod[i][1] - sortedPeriod[0][1]) / periodRange * (lenPeriod / 2.0)
            # print(periodRange)
            if startDate == 10 and endDate == 41:
                print(lenPeriod/2.0)

            midpoint = int(lenPeriod / 2)
            diff = abs(curPeriod[midpoint][1] - curTemplate[midpoint][1])
            for i in range(lenPeriod):
                curPeriod[i][1] = curPeriod[i][1] - diff
                curPeriod[i][0] = i

            acc = fastdtw(curPeriod, curTemplate)
            curSimilarityDist = acc[lenPeriod - 1][lenPeriod - 1]

            if curSimilarityDist <= SIM_THRESHOLD * lenPeriod:
                left = smoothedData[startDate][1]
                right = smoothedData[endDate][1]
                slope = abs(left - right) / min(left, right)
                # if match
                # leftBound = endDate + 1     dateInc = TIMESPAN_MIN    save the arc
                if slope <= CIRCLE_HORIZONTAL_THRESHOLD:
                    distList.append(curSimilarityDist / lenPeriod)
                    dateInc = TIMESPAN_MIN
                    leftBound = endDate + 1
                    pricePatternList.append([startDate, endDate])
                    break

            startDate = startDate - 1

        endDate = endDate + dateInc

    print(pricePatternList)

    plot_flag = False
    count = len(pricePatternList)
    if count == 0:
        print('no matches found')
    elif count == 1:
        print('found 1 match')
        plot_flag = True
    else:
        print('found %d matches' % count)
        plot_flag = True

    if plot_flag:
        plt.figure(figsize=(8, 6), dpi=160)

        closeLine = []
        globalX = []
        for index, row in klineData.iterrows():
            date_time = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
            globalX.append(date2num(date_time))
            closeLine.append(row[2])

        maLine = []
        for e in range(TOTALDATES):
            maLine.append(smoothedData[e][1])

        arc_plot(maLine, globalX, pricePatternList, 'symmetric')
        plt.plot(globalX, closeLine, 'red')
        plt.plot(globalX, maLine, 'green')

        # plt.savefig('%s.png' % stockCode)
        plt.show()
