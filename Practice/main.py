import stream
import day_split
import pandas
import plotting
import indicators
import strategy

if __name__ == '__main__':
    df = pandas.read_csv('history.csv')
    if len(df.index) < 10 ** 6:
        ticker = input('Ввод тикера')
        stream.start_stream(ticker)

    candles_data_frame_1m = pandas.read_csv('candles_1m.csv')
    candles_data_frame_15m = pandas.read_csv('candles_15m.csv')
    candles_data_frame_1h = pandas.read_csv('candles_1h.csv')

    candles_data_frame_1m = candles_data_frame_15m = candles_data_frame_1h =\
        pandas.DataFrame([], columns=['time', 'open', 'close', 'high', 'low', 'volume'])

    for i in day_split.split():
        plotting.ticks_plot(i)
        candles = plotting.candle_plot(i, '1m')
        candles_data_frame_1m = pandas.concat([candles_data_frame_1m, candles], ignore_index=True)
        candles = plotting.candle_plot(i, '15m')
        candles_data_frame_15m = pandas.concat([candles_data_frame_15m, candles], ignore_index=True)
        candles = plotting.candle_plot(i, '60m')
        candles_data_frame_1h = pandas.concat([candles_data_frame_1h, candles], ignore_index=True)

    candles_data_frame_1m.to_csv('candles_1m.csv', index=False)
    candles_data_frame_15m.to_csv('candles_15m.csv', index=False)
    candles_data_frame_1h.to_csv('candles_1h.csv', index=False)

    profit = 0

    for tf in (candles_data_frame_1m, candles_data_frame_15m, candles_data_frame_1h):
        tf = indicators.bollinger_plot(tf)
        tf = indicators.ema_plot(tf)
        tf = indicators.macd(tf)
        tf = indicators.zigzag(tf)

        profit += strategy.positions(tf)

    print(f'Общий профит по всех таймфреймам: {profit}')

