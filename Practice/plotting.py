import matplotlib.pyplot as mpl
import mplfinance as mplf
import pandas
import datetime


def ticks_plot(day: pandas.DataFrame) -> None:
    figure, axis = mpl.subplots()
    axis.plot(day['time'].to_list(), day['price'].to_list())
    mpl.show()


def candle_plot(day: pandas.DataFrame, time_frame: str) -> pandas.DataFrame:
    mc = mplf.make_marketcolors(up='g', down='r', inherit=True)  # Цвет свечей и фитилей

    style_dist = {"xtick.color": '#808097',
                  "ytick.color": '#808097',
                  "xtick.labelcolor": '#808097',
                  "ytick.labelcolor": '#808097',
                  "axes.spines.top": False,
                  "axes.spines.right": False,
                  "axes.labelcolor": '#808097',
                  'scatter.edgecolors': '#000000',
                  'axes.edgecolor': '#000000'}

    day['time'] = day['time'].dt.floor(f'{time_frame.rstrip("m")}min')

    try:
        first_item = day.iloc[0]
    except IndexError:
        print(f'error on {time_frame}')
        return day

    first_price = first_item['price']
    first_time = first_item['time']
    candles = pandas.DataFrame([[first_time -
                                 datetime.timedelta(minutes=first_time.minute % int(time_frame.rstrip('m')),
                                                    seconds=first_time.second,
                                                    microseconds=first_time.microsecond),
                                 first_price,
                                 first_price,
                                 first_price,
                                 first_price,
                                 first_item['qty']]],
                               columns=['time', 'open', 'close', 'high', 'low', 'volume'])

    for i in range(1, len(day)):
        cur_item = day.iloc[i]
        cur_time = cur_item['time']
        last_time = day.iloc[i - 1]['time']
        cur_price = cur_item['price']

        if cur_time.day == last_time.day and cur_time.hour == last_time.hour and \
                cur_time.minute - cur_time.minute % int(time_frame.rstrip('m')) == last_time.minute:
            if cur_price > candles.iloc[-1]['high']:
                candles.at[len(candles.index) - 1, 'high'] = cur_price

            if cur_price < candles.iloc[-1]['low']:
                candles.at[len(candles.index) - 1, 'low'] = cur_price

            candles.at[len(candles.index) - 1, 'volume'] += cur_item['qty']
            candles.at[len(candles.index) - 1, 'close'] = cur_price

        else:
            candles = pandas.concat([candles,
                                     pandas.DataFrame([[cur_time -
                                                        datetime.timedelta(
                                                            minutes=cur_time.minute % int(time_frame.rstrip('m')),
                                                            seconds=cur_time.second,
                                                            microseconds=cur_time.microsecond),
                                                        cur_price,
                                                        cur_price,
                                                        cur_price,
                                                        cur_price,
                                                        cur_item['qty']]], columns=candles.columns)],
                                    ignore_index=True)

    candles = candles.iloc[1:, :7]
    candles.index = pandas.DatetimeIndex(candles['time'])

    s = mplf.make_mpf_style(marketcolors=mc, figcolor='#1C1C23', facecolor='#1C1C23', edgecolor='#808097',
                            rc=style_dist, gridcolor='#3A3A48', gridstyle="--")
    mplf.plot(candles, block=True, ylabel='', type='candle', style=s, title=time_frame, volume=True)

    return candles
