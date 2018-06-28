import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from matplotlib.pylab import num2date
import mpl_finance as mpf


def arc_plot(value, axis, date_index, arc_type):
    for index in date_index:
        print(index[0])
        spline_x = axis[index[0]:index[1] + 1]
        spline_y = value[index[0]:index[1] + 1]
        spline_min = np.min(spline_y) * 1.02

        if arc_type == 'symmetric':
            # spline_min_index = int((spline_x[0] + spline_x[-1]) / 2)
            spline_min_index = spline_x[spline_y.index(min(spline_y))]
        elif arc_type == 'asymmetric':
            spline_min_index = spline_x[spline_y.index(min(spline_y))]
        else:
            spline_min_index = spline_x[spline_y.index(min(spline_y))]

        if spline_min_index >= index[1] - 1:
            spline_min_index = int((spline_x[0] + spline_x[-1]) / 2)

        spline_target_x = [spline_x[0], spline_min_index, spline_min_index + 1, spline_x[-1]]
        spline_target_y = [spline_y[0], spline_min, spline_min, spline_y[-1]]
        spline_itp_x = np.linspace(spline_target_x[0], spline_target_x[-1], num=100, endpoint=True)
        f = interpolate.interp1d(spline_target_x, spline_target_y, kind='quadratic')
        spline_itp_y = f(spline_itp_x)

        horizon_x = [num2date(spline_target_x[0]), num2date(spline_target_x[-1])]
        horizon_y = [spline_y[0], spline_y[-1]]

        plt.plot(horizon_x, horizon_y, 'blue')
        plt.plot(spline_itp_x, spline_itp_y, color='orange')


def kgrid(stock_code, data_list):
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.xaxis_date()
    plt.xticks(rotation=45)
    plt.yticks()
    plt.title("Stock Code: %s" % stock_code)
    plt.xlabel("Time")
    plt.ylabel("Price")
    mpf.candlestick_ochl(ax, data_list, width=0.72, colorup='r', colordown='green')
    plt.grid()
