import numpy as np


def moving_average(series, window, price_type):
    price = []
    length = len(series)
    for e in range(length):
        if price_type == 'ochl_average':
            price.append(np.mean(series.iloc[e][['open', 'close', 'high', 'low']]))
        elif price_type == 'simple':
            price.append(np.mean(series.iloc[e][['open', 'close']]))
        elif price_type == 'close':
            price.append(series.iat[e, 2])
        else:
            price.append(series.iat[e, 2])  # setting default as close

    zipsma = []
    for e in range(length - window + 1):
        sma = np.mean(price[e:e + window])
        date = series.iat[e + window - 1, 0]
        zipsma.append([date, sma])

    return zipsma
