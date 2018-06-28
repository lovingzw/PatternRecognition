# Version 0.2.0


import datetime
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
import copy
import tushare as ts
from dtw import fastdtw
from arc import arc_circle_gen
from sma import moving_average
from simpleplot import arc_plot

stockCode = '300682'
startDate = '2018-03-01'
endDate = '2018-06-31'
window = 5
similarity_threshold = 3
horizon_threshold = 0.02

if __name__ == '__main__':
    klineData = ts.get_k_data(stockCode, start=startDate, end=endDate)
    smoothedHistory = moving_average(klineData, window, 'close')  # losing first (window - 1) data

    historyLength = len(smoothedHistory)

    # key, start_day, end_day, similarity/time_span ratio
    pricePatternList = []
    # start_day, end_day
    savePatternList = []
    # key, start_day
    pricePtnStartInfo = []
    # key, end_day
    pricePtnEndInfo = []
    # key
    patternKey = 0

    pricePtnUsed = []

    for arcLength in range(21, 41):
        # arcLength = 30
        circleRadius = arcLength / 2.0
        dateIndex = []
        sim_list = []
        alternative = []

        template = arc_circle_gen(arcLength, circleRadius)

        # scanning 1 stock through time
        for i in range(historyLength - arcLength + 1):

            smoothedSample = copy.deepcopy(smoothedHistory[i:i + arcLength])

            # normalized smoothedSample
            sortedSmoothedSample = sorted(smoothedSample, key=lambda smoothedSample: smoothedSample[1])
            priceRange = sortedSmoothedSample[arcLength - 1][1] - sortedSmoothedSample[0][1]
            priceLow = sortedSmoothedSample[0][1]
            for j in range(arcLength):
                smoothedSample[j][1] = (smoothedSample[j][1] - priceLow) / priceRange * circleRadius

            midpoint = int(arcLength / 2)
            diff = abs(smoothedSample[midpoint][1] - template[midpoint][1])

            for e in range(arcLength):
                smoothedSample[e][1] = smoothedSample[e][1] - diff
                smoothedSample[e][0] = e

            acc = fastdtw(smoothedSample, template)
            similarity_distance = acc[arcLength - 1][arcLength - 1]
            sim_list.append(similarity_distance)

            if similarity_distance < similarity_threshold * arcLength:
                left = klineData.iat[i + window - 1, 2]
                right = klineData.iat[i + arcLength + window - 2, 2]

                slope = abs(left - right) / min(left, right)
                if slope <= horizon_threshold:
                    dateIndex.append(i)  # dateIndex[0] = klineData[4]

                    # record the pattern found under current time span
                    startday = int(date2num(datetime.datetime.strptime(klineData.iat[i + window - 1, 0], '%Y-%m-%d')))
                    endday = int(
                        date2num(datetime.datetime.strptime(klineData.iat[i + arcLength + window - 2, 0], '%Y-%m-%d')))
                    pricePatternList.append([patternKey, startday, endday, similarity_distance * 1.0 / arcLength])
                    pricePtnStartInfo.append([patternKey, startday, endday])
                    pricePtnEndInfo.append([patternKey, endday, startday])
                    pricePtnUsed.append(False)
                    patternKey = patternKey + 1

                    print('arc length:', arcLength, ',day %d similarity:' % i, similarity_distance)

    pricePatternList = sorted(pricePatternList, key=lambda pricePatternList: pricePatternList[3])
    pricePatternList.reverse()
    pricePtnStartInfo = sorted(pricePtnStartInfo, key=lambda pricePtnStartInfo: pricePtnStartInfo[1])
    pricePtnEndInfo = sorted(pricePtnEndInfo, key=lambda pricePtnEndInfo: pricePtnEndInfo[1])

    for i in range(patternKey):
        # unused price pattern
        if not pricePtnUsed[pricePatternList[i][0]]:
            pricePtnUsed[pricePatternList[i][0]] = True
            cur_start = pricePatternList[i][1]
            cur_end = pricePatternList[i][2]
            savePatternList.append([cur_start, cur_end])
            # delete those whose start time in the current time span
            # should be replaced with bisection
            for j in range(patternKey):
                if pricePtnStartInfo[j][1] > cur_end:
                    break
                if pricePtnStartInfo[j][1] <= cur_start <= pricePtnStartInfo[j][2]:
                    pricePtnUsed[pricePtnStartInfo[j][0]] = True
                elif pricePtnStartInfo[j][1] <= cur_end:
                    pricePtnUsed[pricePtnStartInfo[j][0]] = True

    count = len(savePatternList)


    if count == 0:
        print('no matches found')
        plot_flag = False
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
        closeLine = closeLine[window - 1:]
        globalX = globalX[window - 1:]
        plt.plot(globalX, closeLine, 'red')

        maLine = []
        for e in range(historyLength):
            maLine.append(smoothedHistory[e][1])
        plt.plot(globalX, maLine, 'green')

        for e in savePatternList:
            e[0] = globalX.index(e[0])
            e[1] = globalX.index(e[1])
        arc_plot(closeLine, globalX, savePatternList, 'symmetric')

        # plt.savefig('%s.png' % stockCode)
        plt.show()
