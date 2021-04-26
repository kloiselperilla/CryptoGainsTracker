from datetime import datetime, date
import json
from Historic_Crypto import HistoricalData

ONE_DAY = 86400
ONE_HOUR = 3600
FILE_FORMAT = '{currency_pair}_{interval}_data.json'


class PriceHistory:
    def __init__(self, currency_pair, interval, start='2017-01-01-00-00'):
        # new = HistoricalData('BTC-USD',86400,'2017-01-01-00-00').retrieve_data()
        self.currency_pair = currency_pair
        self.interval = interval
        self.date_format = self._date_format_for_interval(interval)
        self.history_dict = self._get_history(currency_pair, interval, start)

    def __getitem__(self, date):
        return self.history_dict[date.strftime(self.date_format)]

    def __setitem__(self, date, price):
        self.history_dict[date.strftime(self.date_format)] = price

    def _date_format_for_interval(self, interval):
        if interval == ONE_DAY:
            date_format = '%Y-%m-%d'
        elif interval == ONE_HOUR:
            date_format = '%Y-%m-%d,%H:00:00'
        else:
            raise Exception('Unsupported interval')
        return date_format

    def _get_history(self, currency_pair, interval, start):
        path_name = FILE_FORMAT.format(currency_pair=currency_pair, interval=interval)
        try:
            with open(path_name) as f:
                print('Using saved data')
                history_dict = json.load(f)
        except FileNotFoundError:
            print('No save data found\nPulling data...')
            dat = HistoricalData(currency_pair, interval, start).retrieve_data()
            hist = {}
            for index, row in dat.iterrows():
                hist[row.name.strftime(self.date_format)] = row['close']
            self._save_history(hist, path_name)
            history_dict = hist
        return history_dict

    def _save_history(self, history, path_name):
        with open(path_name, 'w') as fp:
            json.dump(history, fp)
