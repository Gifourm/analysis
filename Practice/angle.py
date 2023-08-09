import asyncio
import pandas
import talib
from sklearn.linear_model import LinearRegression
import numpy as np
import websockets
from json import loads


async def angle(ticks: pandas.DataFrame) -> None:
    while True:
        breaker = False
        ticks = ticks.iloc[:, :2]
        ticks.columns = ['time', 'price']
        ticks['index'] = range(len(ticks.index))

        dev = []
        for timeperiod in range(1000, int(len(ticks.index) / 2), 1000):
            dev.append([])
            for i in range(timeperiod, len(ticks.index), timeperiod):
                x = np.array(ticks.iloc[i - timeperiod:i]['index']).reshape((-1, 1))
                y = np.array(ticks.iloc[i - timeperiod:i]['price'])
                model = LinearRegression().fit(x, y)
                dev[int(timeperiod / 1000) - 1].append(model.score(x, y))

        for item in range(len(dev)):
            dev[item] = sum(dev[item]) / len(dev[item])

        max_r = max(dev)
        timeperiod = 1000 * dev.index(max_r) + 1000
        last_angle = 0
        last_intercept = 0

        for i in range(timeperiod, len(ticks.index), timeperiod):
            x = np.array(ticks.iloc[i - timeperiod:i]['index']).reshape((-1, 1))
            y = np.array(ticks.iloc[i - timeperiod:i]['price'])
            model = LinearRegression().fit(x, y)
            last_angle = model.coef_[0]
            last_intercept = model.intercept_

        reduced_angle = last_angle / ticks.iat[1000, 1] * 10 ** 9 * timeperiod / len(ticks.index)
        data_len = len(ticks.index)
        counter = 0
        last_price = 0
        long = short = False
        method = f'{ticker.lower()}@aggTrade'
        url = f'wss://fstream.binance.com/ws/{method}'
        async with websockets.connect(url) as trade_stream:
            while not breaker:
                trade = loads(await trade_stream.recv())
                price = float(trade['p'])
                counter += 1
                ticks['stddev'] = talib.STDDEV(ticks.iloc[-timeperiod:]['price'], timeperiod=timeperiod)
                std_dev = ticks.iloc[-1]['stddev']

                if not long and not short and abs(price - (last_angle * (counter + data_len) + last_intercept)) > \
                        abs(std_dev * 2):
                    breaker = True

                elif reduced_angle >= 6 and price > last_angle * (counter + data_len) + last_intercept > last_price\
                        and not long:
                    with open('trades.txt', 'a') as file:
                        file.write(f'Точка входа в лонг-позицию: {price}')
                    long = True
                    buy_price = price

                elif reduced_angle <= -6 and price < last_angle * (counter + data_len) + last_intercept < last_price\
                        and not short:
                    with open('trades.txt', 'a') as file:
                        file.write(f'Точка входа в шорт-позицию: {price}')
                    short = True
                    sell_price = price

                elif (long or short) and abs(price - (last_angle * (counter + data_len) + last_intercept)) > \
                        abs(std_dev * 2):
                    if long:
                        with open('trades.txt', 'a') as file:
                            file.write(f'Закрыта лонг-позиция по цене: {price}\nROE позиции: {price / buy_price - 1}')
                        long = False

                    if short:
                        with open('trades.txt', 'a') as file:
                            file.write(f'Закрыта шорт-позиция по цене: {price}\nROE позиции: {sell_price / price - 1}')
                        short = False

                last_price = price

        ticks = pandas.read_csv(f'history_{ticker}_ticks.csv')


if __name__ == '__main__':
    ticker = 'ETHBUSD'
    df = pandas.read_csv(f'history_{ticker}_ticks.csv')
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(angle(df))

