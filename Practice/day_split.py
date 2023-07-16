import pandas
import datetime


def split() -> pandas.DataFrame:
    data_frame = pandas.read_csv('history.csv')
    data_frame['time'] = pandas.to_datetime(data_frame['time'], origin='unix', unit='ms') + datetime.timedelta(hours=3)

    for i in range(int(data_frame.iloc[-1]['time'].day - data_frame.iloc[0]['time'].day)):
        yield data_frame[data_frame["time"].dt.day == data_frame.iloc[0]['time'].day + i]

