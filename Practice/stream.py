import websockets
import asyncio
from json import loads
import csv


async def stream(ticker: str) -> None:
    method = f'{ticker.lower()}@aggTrade'
    url = f'wss://fstream.binance.com/ws/{method}'
    last_price = 0
    async with websockets.connect(url) as trade_stream:
        for i in range(10 ** 6):
            trade = loads(await trade_stream.recv())
            with open('history.csv', 'a', encoding='utf-8') as w_file:
                writer = csv.DictWriter(w_file, delimiter=',', lineterminator="\r", fieldnames=['time', 'price',
                                                                                                'qty', 'side'])
                writer.writerow({'time': trade['T'],
                                 'price': trade['p'],
                                 'qty': trade['q'],
                                 'side': 'long' if float(trade['p']) > float(last_price) else 'short'})

                last_price = trade['p']


def start_stream(symbol: str):
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(stream(symbol))


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    symbol = input()
    loop.run_until_complete(stream(symbol))
