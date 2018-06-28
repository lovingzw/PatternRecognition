# Version 0.3.0
# specific dates can be withdrawn by klineData.iat[i, 0].


import datetime
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num, num2date
from matplotlib.dates import DateFormatter, MonthLocator, DayLocator, MONDAY,YEARLY
import copy
import tushare as ts
from dtw import fastdtw
from arc import arc_circle_gen
from sma import moving_average
from simpleplot import arc_plot

stockCode = '300682'
startDate = '2017-01-01'
endDate = '2018-06-31'
window = 5
arcRange = [21, 40]
similarity_threshold = 2
horizon_threshold = 0.02


if __name__ == '__main__':
    klineData = ts.get_k_data(stockCode, start=startDate, end=endDate)
    smoothedHistory = moving_average(klineData, window, 'close')  # losing first (window - 1) data
    klineData = klineData.iloc[window-1:]

    historyLength = len(smoothedHistory)

    # [key, start_day, end_day, similarity/time_span ratio]
    pricePatternList = []
    # [start_day, end_day]
    savePatternList = []
    # [key, start_day]
    pricePtnStartInfo = []
    # [key, end_day]
    pricePtnEndInfo = []
    # key
    patternKey = 0

    pricePtnUsed = []

    for arcLength in range(arcRange[0], arcRange[1]+1):
        # arcLength = 30
        circleRadius = arcLength / 2.0
        dateIndex = []
        sim_list = []
        alternative = []

        template = arc_circle_gen(arcLength, circleRadius)

        # scanning 1 stock through time
        for i in range(historyLength - arcLength + 1):

            smoothedSample = copy.deepcopy(smoothedHistory[i:i + arcLength])
            normalizedSmoothedSample = copy.deepcopy(smoothedSample)

            # normalized smoothedSample
            sortedSmoothedSample = sorted(smoothedSample, key=lambda smoothedSample: smoothedSample[1])
            priceRange = sortedSmoothedSample[arcLength - 1][1] - sortedSmoothedSample[0][1]
            priceLow = sortedSmoothedSample[0][1]
            for j in range(arcLength):
                normalizedSmoothedSample[j][1] = (smoothedSample[j][1] - priceLow) / priceRange * circleRadius

            midpoint = int(arcLength / 2)
            diff = abs(normalizedSmoothedSample[midpoint][1] - template[midpoint][1])

            for j in range(arcLength):
                normalizedSmoothedSample[j][1] = normalizedSmoothedSample[j][1] - diff
                normalizedSmoothedSample[j][0] = j

            acc = fastdtw(normalizedSmoothedSample, template)
            similarity_distance = acc[arcLength - 1][arcLength - 1]
            sim_list.append(similarity_distance)

            if similarity_distance < similarity_threshold * arcLength:

                left = smoothedSample[0][1]
                right = smoothedSample[-1][1]
                slope = abs(left - right) / min(left, right)

                if slope <= horizon_threshold:
                    dateIndex.append(i)

                    # record the pattern found under current time span
                    startday = i
                    endday = i + arcLength - 1
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
            print(pricePatternList[i][3])
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

    print(savePatternList)

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

        monthdays = MonthLocator()
        alldays = DayLocator()

        plt.figure(figsize=(8, 6), dpi=160)
        closeLine = []
        globalX = []

        for index, row in klineData.iterrows():
            date_time = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
            # globalX.append(date_time)
            globalX.append(date2num(date_time))
            closeLine.append(row[2])

        maLine = []
        for i in range(historyLength):
            maLine.append(smoothedHistory[i][1])

        arc_plot(maLine, globalX, savePatternList, 'symmetric')
        plt.plot(globalX, closeLine, 'red')
        plt.plot(globalX, maLine, 'green')

        # plt.savefig('%s.png' % stockCode)
        plt.show()
