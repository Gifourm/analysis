import pandas
import talib
import numpy as np
import os
import mplfinance as mplf
from indicators import set_style
import indicators
from indicators import reset_index


def smooth(trades: pandas.DataFrame) -> pandas.DataFrame:
    try:
        ticks = [trades.iat[0, 1]]
        qtys = [trades.iat[0, 2]]

    except KeyError:
        trades.columns = ['time', 'price', 'qty', 'side']
        ticks = [trades.iat[0, 1]]
        qtys = [trades.iat[0, 2]]

    last_change = 'up'
    timeperiod = 500

    if not os.path.isfile('smoothed_ticks.csv'):
        for i in range(1, len(trades.index)):
            cur_price = trades.iat[i, 1]
            last_price = trades.iat[i - 1, 1]

            if cur_price == last_price:
                qtys[-1] += trades.iat[i, 2]
                continue

            if cur_price > last_price and last_change != 'up':
                ticks.append(cur_price)
                last_change = "up"
                qtys.append(trades.iat[i, 2])

            elif cur_price < last_price and last_change != 'down':
                ticks.append(cur_price)
                last_change = 'down'
                qtys.append(trades.iat[i, 2])

            else:
                ticks[-1] = cur_price

        ticks = np.array(ticks)
        ticks = pandas.DataFrame({"price": ticks, "SMA": talib.SMA(ticks, timeperiod=timeperiod), 'qty': qtys})
        mean_diff = ((ticks['price'] - ticks['SMA']) ** 2).mean()

        smoothed_ticks = ticks

        for i in range(len(ticks.index)):
            try:
                if abs(ticks.iat[i, 0] - ticks.iat[i, 1]) > 1.4 * mean_diff:
                    smoothed_ticks = smoothed_ticks.drop(i)
            except IndexError:
                break

        smoothed_ticks.reset_index(drop=True, inplace=True)
        smoothed_ticks.to_csv('smoothed_ticks.csv', index=False)

    else:
        smoothed_ticks = pandas.read_csv('smoothed_ticks.csv')

    return smoothed_ticks


def ticks_to_candles(smoothed_ticks: pandas.DataFrame) -> pandas.DataFrame:
    if os.path.isfile('candles_ticks.csv'):
        candles_ticks = pandas.read_csv('candles_ticks.csv')
    else:
        first_item = smoothed_ticks.iat[0, 0]
        candles_ticks = pandas.DataFrame([[first_item, first_item, first_item, first_item, smoothed_ticks.iat[0, 2]]],
                                         columns=["open", "close", "high", 'low', 'volume'])
        for i in range(len(smoothed_ticks.index)):
            cur_price = smoothed_ticks.iat[i, 0]
            if i % 1000 == 0:
                candles_ticks.loc[len(candles_ticks)] = {"open": cur_price,
                                                         "close": cur_price,
                                                         "high": cur_price,
                                                         'low': cur_price,
                                                         'volume': smoothed_ticks.iat[i, 2]}
            else:
                if cur_price > candles_ticks.iat[len(candles_ticks) - 1, 2]:
                    candles_ticks.iat[len(candles_ticks) - 1, 2] = cur_price

                if cur_price < candles_ticks.iat[len(candles_ticks) - 1, 3]:
                    candles_ticks.iat[len(candles_ticks) - 1, 3] = cur_price

                    candles_ticks.iat[len(candles_ticks) - 1, 1] = cur_price
                    candles_ticks.iat[len(candles_ticks) - 1, 4] += smoothed_ticks.iat[i, 2]

        candles_ticks.to_csv('candles_ticks.csv', index=False)

        candles_ticks = reset_index(candles_ticks)

        s, style_dict = set_style()
        mplf.plot(candles_ticks, block=True, ylabel='', type='candle', style=s, warn_too_much_data=1000000)

    return candles_ticks


def flat_n_trend(candles_ticks: pandas.DataFrame) -> (pandas.DataFrame, str):
    timeperiod = 20
    candles_ticks.reset_index(drop=True, inplace=True)
    candles_ticks['SMA'] = talib.SMA((candles_ticks['high'] + candles_ticks['low']) / 2, timeperiod=timeperiod)

    candles_ticks['jaw'] = np.nan
    candles_ticks['teeth'] = np.nan
    candles_ticks['lips'] = np.nan
    candles_ticks.iat[timeperiod + int(timeperiod * 0.15), -3] = candles_ticks.iat[timeperiod, 5]
    print('5')
    print(candles_ticks.iat[timeperiod, 5])
    candles_ticks.iat[timeperiod + int(timeperiod * 0.25), -2] = candles_ticks.iat[timeperiod, 5]
    candles_ticks.iat[timeperiod + int(timeperiod * 0.4), -1] = candles_ticks.iat[timeperiod, 5]

    print(candles_ticks)
    for i in range(timeperiod + 1, len(candles_ticks.index)):
        if i + int(timeperiod * 0.4) >= len(candles_ticks):
            candles_ticks.loc[len(candles_ticks)] = {}

        candles_ticks.iat[i + int(timeperiod * 0.15), -3] = (candles_ticks.iat[i + int(timeperiod * 0.15) - 1, -3] * (
                timeperiod * 0.25 - 1) + (candles_ticks.iat[i, 2] + candles_ticks.iat[i, 3]) / 2) / (timeperiod *
                                                                                                     0.25)
        candles_ticks.iat[i + int(timeperiod * 0.25), -2] = (candles_ticks.iat[i + int(timeperiod * 0.25) - 1, -2] * (
                timeperiod * 0.4 - 1) + (candles_ticks.iat[i, 2] + candles_ticks.iat[i, 3]) / 2) / (timeperiod *
                                                                                                    0.4)
        candles_ticks.iat[i + int(timeperiod * 0.4), -1] = (candles_ticks.iat[i + int(timeperiod * 0.4) - 1, -1] * (
                timeperiod * 0.65 - 1) + (candles_ticks.iat[i, 2] + candles_ticks.iat[i, 3]) / 2) / (timeperiod *
                                                                                                     0.65)

    candles_ticks['index'] = range(len(candles_ticks))
    candles_ticks['index'] = pandas.to_datetime(candles_ticks['index'])

    change_directions = []
    depth = 10
    direction = None
    for i in range(len(candles_ticks.index)):
        cur_jaw = candles_ticks.iat[i, -4]
        cur_teeth = candles_ticks.iat[i, -3]
        cur_lips = candles_ticks.iat[i, -2]

        last_jaw = candles_ticks.iat[i - 1, -4]
        last_teeth = candles_ticks.iat[i - 1, -3]
        last_lips = candles_ticks.iat[i - 1, -2]

        prev_jaw = candles_ticks.iat[i - 2, -4]
        prev_teeth = candles_ticks.iat[i - 2, -3]
        prev_lips = candles_ticks.iat[i - 2, -2]

        if abs(cur_lips - cur_teeth) < abs(last_lips - last_teeth) < abs(prev_lips - prev_teeth) and depth > 10 and \
                abs(cur_teeth - cur_jaw) < abs(last_teeth - last_jaw) < abs(
            prev_teeth - prev_jaw) and direction != 'flat':
            change_directions.append(candles_ticks.iat[i, -1])
            depth = 0
            direction = 'flat'

        elif abs(cur_lips - cur_teeth) > abs(last_lips - last_teeth) > abs(prev_lips - prev_teeth) and depth > 10 and \
                abs(cur_teeth - cur_jaw) > abs(last_teeth - last_jaw) > abs(
            prev_teeth - prev_jaw) and direction != 'trend':
            change_directions.append(candles_ticks.iat[i, -1])
            depth = 0
            direction = "trend"

        else:
            depth += 1

    candles_ticks.to_csv('candles_ticks_alligator.csv', index=False)

    candles_ticks = reset_index(candles_ticks)
    # alligator_addplot = [mplf.make_addplot(candles_ticks['jaw'], color='b', markersize=1, width=1),
    #                      mplf.make_addplot(candles_ticks['teeth'], color='r', markersize=1, width=1),
    #                      mplf.make_addplot(candles_ticks['lips'], color='g', markersize=1, width=1)]

    s, style_dict = set_style()
    mplf.plot(candles_ticks, block=True, ylabel='', type='candle', style=s, warn_too_much_data=1000000,
              vlines=dict(vlines=change_directions, linewidths=1, alpha=0.4))

    return candles_ticks, direction


if __name__ == '__main__':
    smoothed_ticks = smooth(pandas.read_csv('old history/history.csv'))
    candles_ticks = ticks_to_candles(smoothed_ticks)
    directions = flat_n_trend(candles_ticks)
    indicators.rsi(candles_ticks)
    indicators.adx(candles_ticks)
    indicators.mfi(candles_ticks)
    indicators.cci(candles_ticks)
