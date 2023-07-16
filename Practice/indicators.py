import numpy as np
import pandas
import talib
import mplfinance as mplf


def set_style() -> (dict, dict):
    mc = mplf.make_marketcolors(up='g', down='r', inherit=True)
    style_dict = {"xtick.color": '#808097',
                  "ytick.color": '#808097',
                  "xtick.labelcolor": '#808097',
                  "ytick.labelcolor": '#808097',
                  "axes.spines.top": False,
                  "axes.spines.right": False,
                  "axes.labelcolor": '#808097',
                  'scatter.edgecolors': '#000000',
                  'axes.edgecolor': '#000000'}

    s = mplf.make_mpf_style(marketcolors=mc, figcolor='#1C1C23', facecolor='#1C1C23', edgecolor='#808097',
                            rc=style_dist, gridcolor='#3A3A48', gridstyle="--")
    return s, style_dict


def bollinger_plot(candles: pandas.DataFrame) -> pandas.DataFrame:
    s, style_dict = set_style()

    candles['upper_bollinger'], candles['middle_bollinger'], candles['lower_bollinger'] = \
        talib.BBANDS(candles['close'], 30, 2.84, 2.84)

    bollinger_addplot = [mplf.make_addplot(candles['upper_bollinger'], color='r', markersize=1, width=1),
                         mplf.make_addplot(candles['middle_bollinger'], color='b', markersize=1, width=1),
                         mplf.make_addplot(candles['lower_bollinger'], color='g', markersize=1, width=1)]

    candles.index = pandas.DatetimeIndex(candles['time'])
    candles = candles.iloc[2:, 1:8]
    try:
        mplf.plot(candles, block=True, ylabel='', type='candle', style=s, title='BBands', volume=True,
                  addplot=bollinger_addplot, warn_too_much_data=1000000)
    except ValueError:
        pass

    return candles


def ema_plot(candles: pandas.DataFrame) -> pandas.DataFrame:
    s, style_dict = set_style()

    candles['short_ema'] = talib.EMA(candles['close'], timeperiod=30)
    candles['long_ema'] = talib.EMA(candles['close'], timeperiod=70)

    ema_addplot = [mplf.make_addplot(candles['short_ema'], color='y', markersize=1, width=1),
                   mplf.make_addplot(candles['long_ema'], color='b', markersize=1, width=1)]

    candles.index = pandas.DatetimeIndex(candles['time'])
    try:
        mplf.plot(candles, block=True, ylabel='', type='candle', style=s, title='EMA', volume=True,
                  addplot=ema_addplot, warn_too_much_data=1000000)
    except ValueError:
        pass

    return candles


def macd(candles: pandas.DataFrame) -> pandas.DataFrame:
    s, style_dict = set_style()

    candles['MACD'], candles['MACDSignal'], candles['MACDhist'] = talib.MACD(candles['close'], fastperiod=12,
                                                                             slowperiod=26,
                                                                             signalperiod=9)

    macd_addplot = [mplf.make_addplot(candles['MACD'], color='w', markersize=1, panel=2, width=1),
                    mplf.make_addplot(candles['MACDSignal'], color='b', markersize=1, panel=2, width=1),
                    mplf.make_addplot(candles['MACDhist'], color='r', markersize=1, panel=2, width=1)]

    candles.index = pandas.DatetimeIndex(candles['time'])
    try:
        mplf.plot(candles, block=True, ylabel='', type='candle', style=s, title='MACD', volume=True,
                  addplot=macd_addplot, warn_too_much_data=1000000)
    except ValueError:
        pass

    return candles


def zigzag(candles: pandas.DataFrame) -> pandas.DataFrame:
    s, style_dict = set_style()

    candles['zigzag'] = np.nan
    last_point = candles.iloc[0]['open']
    candles.iat[0, 14] = last_point
    depth = 1
    last_change = None

    for i in range(1, len(candles.index)):
        current_item = candles.iloc[i]
        if (current_item['high'] > last_point * 1.01 and depth >= 3) or \
                (last_change != 'low' and current_item['high'] > last_point):
            if last_change != 'low' and current_item['high'] > last_point:
                for j in range(i, 1, -1):
                    if str(candles.iat[j, 14]) != str(np.nan):
                        candles.iat[j, 14] = np.nan
                        break
            depth = 1
            last_change = 'high'
            last_point = current_item['high']
            candles.iat[i, 14] = last_point

        elif (current_item['low'] * 1.01 < last_point and depth >= 3) or \
                (last_change != 'high' and current_item['low'] < last_point):
            if last_change != 'high' and current_item['low'] < last_point:
                for j in range(i, 0, -1):
                    if str(candles.iat[j, 14]) != str(np.nan):
                        candles.iat[j, 14] = np.nan
                        break

            depth = 1
            last_change = 'low'
            last_point = current_item['low']
            candles.iat[i, 14] = last_point

        else:
            depth += 1

    if last_change == 'low':
        candles.iat[len(candles.index) - 1, 14] = candles.iloc[-1]['high']
    else:
        candles.iat[len(candles.index) - 1, 14] = candles.iloc[-1]['low']

    line_list = []
    for i in range(len(candles.index)):
        if str(candles.iat[i, 14]) != str(np.nan):
            line_list.append((candles.iat[i, 0], candles.iat[i, 14]))

    candles.index = pandas.DatetimeIndex(candles['time'])
    try:
        mplf.plot(candles, block=True, ylabel='', type='candle', style=s, title='Zigzag', volume=True,
                  alines=dict(alines=line_list, colors='b', linewidths=(0.5,)), warn_too_much_data=1000000)
    except ValueError:
        pass

    return candles
