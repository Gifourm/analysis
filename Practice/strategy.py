import numpy as np
import pandas
import mplfinance as mplf


def positions(candles: pandas.DataFrame) -> float:
    candles['open_position'] = np.nan
    candles['close_position'] = np.nan
    long_opened = False

    for i in range(len(candles.index)):
        current_item = candles.iloc[i]
        last_item = candles.iloc[i - 1]
        prelast_item = candles.iloc[i - 2]

        try:
            if current_item['high'] > current_item['lower_bollinger'] and \
                    last_item['low'] < last_item['lower_bollinger'] and \
                    prelast_item['low'] < prelast_item['lower_bollinger'] and not long_opened:
                candles.at[current_item['time'], 'open_position'] = current_item['lower_bollinger']
                long_opened = True

            if current_item['MACDSignal'] > current_item['MACD'] and last_item['MACDSignal'] < last_item['MACD'] < 0\
                    and current_item['MACD'] < 0 and not long_opened and \
                    prelast_item['MACDSignal'] > prelast_item['MACD']:
                candles.at[current_item['time'], 'open_position'] = current_item['close']
                long_opened = True

            if current_item['close'] > current_item['upper_bollinger'] and \
                    last_item['high'] > last_item['upper_bollinger'] and \
                    prelast_item['close'] < prelast_item['upper_bollinger'] and long_opened:
                candles.at[current_item['time'], 'close_position'] = current_item['close']
                long_opened = False

        except IndexError:
            continue

    mc = mplf.make_marketcolors(up='g', down='r', inherit=True)
    style_dist = {"xtick.color": '#808097',
                  "ytick.color": '#808097',
                  "xtick.labelcolor": '#808097',
                  "ytick.labelcolor": '#808097',
                  "axes.spines.top": False,
                  "axes.spines.right": False,
                  "axes.labelcolor": '#808097',
                  'scatter.edgecolors': '#000000',
                  'axes.edgecolor': '#000000'}

    markers = [mplf.make_addplot(candles['open_position'], type='scatter', marker='^', markersize=140, color='g'),
               mplf.make_addplot(candles['close_position'], type='scatter', marker='v', markersize=140, color='r'),
               mplf.make_addplot(candles['upper_bollinger'], color='r', markersize=1, width=1),
               mplf.make_addplot(candles['middle_bollinger'], color='b', markersize=1, width=1),
               mplf.make_addplot(candles['lower_bollinger'], color='g', markersize=1, width=1)
               ]

    s = mplf.make_mpf_style(marketcolors=mc, figcolor='#1C1C23', facecolor='#1C1C23', edgecolor='#808097',
                            rc=style_dist, gridcolor='#3A3A48', gridstyle="--")

    candles.index = pandas.DatetimeIndex(candles['time'])
    try:
        mplf.plot(candles, block=True, ylabel='', type='candle', style=s, title='Signals', volume=False,
                  addplot=markers, warn_too_much_data=1000000)
    except ValueError:
        print('Нет позиций')

    total_profit = 0
    long_counter = 0
    short_counter = 0
    pandas.set_option('display.max_rows', None)

    for i in range(len(candles.index)):
        if str(candles.iloc[i]['open_position']) != str(np.nan):
            total_profit -= candles.iloc[i]['open_position']
            long_counter += 1

        if str(candles.iloc[i]['close_position']) != str(np.nan):
            total_profit += candles.iloc[i]['close_position']
            short_counter += 1

    if long_counter > short_counter:
        total_profit += candles.iloc[-1]['close']

    total_roe = total_profit / candles.iloc[-1]['close'] * 100
    with_fees = total_roe - (long_counter + short_counter) * 0.02
    print(f'Результирующий ожидаемый профит: {total_roe}\nС учетом комиссий: {with_fees}')

    return with_fees
