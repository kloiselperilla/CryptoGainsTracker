from datetime import datetime
import mock
from order import Order
from price_history import PriceHistory


class TestFromRow:
    test_row_1 = {
        'BTC Volume': '1.2',
        'Ticker': 'BTC',
        'Currency': 'USD',
        'Price': '1234.5',
        'Date': '2018-01-01 00:00:00 +0000',
        'BTC Buy/Sell': 'BUY',
    }
    test_row_2 = {
        'BTC Volume': '1.2',
        'Ticker': 'LTC',
        'Currency': 'BTC',
        'Price': '0.001',
        'Date': '2018-01-01 00:00:00 +0000',
        'BTC Buy/Sell': 'BUY',
    }

    def test_use_included_price_if_correct_currency_pair(self):
        row = self.test_row_1

        ord = Order.from_row(row, 'BTC', mock.MagicMock())

        assert ord.price == 1234.5

    def test_use_price_history_if_incorrect_pair(self):
        row = self.test_row_2
        test_ph = mock.MagicMock()
        test_ph.__getitem__.return_value = 432.1

        ord = Order.from_row(row, 'BTC', test_ph)

        assert ord.price == 432.1

    def test_gets_data_correctly(self):
        row = self.test_row_1

        ord = Order.from_row(row, 'BTC', mock.MagicMock())

        assert ord.currency == 'BTC'
        assert ord.volume == float(row['BTC Volume'])
        assert ord.date == datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S +0000')
        assert ord.type == row['BTC Buy/Sell']
