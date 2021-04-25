from datetime import datetime
import json
import mock
import pytest

from price_history import PriceHistory, ONE_HOUR, ONE_DAY


class TestingPriceHistory(PriceHistory):
    def __init__(self, interval):
        self.history_dict = {}
        self.date_format = self._date_format_for_interval(interval)


@mock.patch('price_history.PriceHistory._get_history')
class TestGetSet:
    def test_getting_set_items_matches_for_rounded_dates_with_day_interval(self, mock_get_hist):
        mock_get_hist.return_value = {}
        ph = PriceHistory('BTC-USD', ONE_DAY)
        date_a = datetime.strptime('2018-06-29 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_b = datetime.strptime('2019-03-10 00:00:00', '%Y-%m-%d %H:%M:%S')
        expected_a = 123.4
        expected_b = 432.1
        ph[date_a] = expected_a
        ph[date_b] = expected_b

        actual_a = ph[date_a]
        actual_b = ph[date_b]

        assert expected_a == actual_a
        assert expected_b == actual_b

    def test_getting_set_items_matches_for_rounded_dates_with_hour_interval(self, mock_get_hist):
        mock_get_hist.return_value = {}
        ph = PriceHistory('BTC-USD', ONE_HOUR)
        date_a = datetime.strptime('2018-06-29 02:00:00', '%Y-%m-%d %H:%M:%S')
        date_b = datetime.strptime('2018-06-29 05:00:00', '%Y-%m-%d %H:%M:%S')
        expected_a = 123.4
        expected_b = 432.1
        ph[date_a] = expected_a
        ph[date_b] = expected_b

        actual_a = ph[date_a]
        actual_b = ph[date_b]

        assert expected_a == actual_a
        assert expected_b == actual_b


@mock.patch('price_history.HistoricalData')
class TestInit:
    def test_raise_error_with_unsupported_interval(self, mock_history):
        with pytest.raises(Exception):
            PriceHistory('BTC-USD', 1234)

    @mock.patch('builtins.open', mock.mock_open(read_data=json.dumps({'a': 'b'})))
    def test_use_file_history_if_exists(self, mock_history):
        ph = PriceHistory('BTC-USD', ONE_HOUR)

        assert ph.history_dict['a'] == 'b'

    @mock.patch('builtins.open', side_effect=FileNotFoundError)
    @mock.patch('price_history.PriceHistory._save_history')
    def test_use_crypto_data_api_if_file_dne(self, mock_save, mock_open, mock_history):
        row_a = mock.MagicMock()
        date_a = datetime.strptime('2018-06-29 00:00:00', '%Y-%m-%d %H:%M:%S')
        row_a.name = date_a

        row_a.__getitem__.return_value = 123.4
        row_b = mock.MagicMock()
        date_b = datetime.strptime('2018-06-30 00:00:00', '%Y-%m-%d %H:%M:%S')
        row_b.name = date_b
        row_b.__getitem__.return_value = 234.5
        iter_dummy = [(0, row_a), (1, row_b)]
        mock_history.return_value.retrieve_data.return_value.iterrows.return_value = iter_dummy

        ph = PriceHistory('BTC-USD', ONE_HOUR)

        assert ph[date_a] == 123.4
        assert ph[date_b] == 234.5

    # def test_saves_file_after_crypto_api(self, mock_history, mock_open):
    #     pass

    # def test_dict_keys_use_one_day_format(self, mock_history, mock_open):
    #     pass

    # def test_dict_keys_use_one_hour_format(self, mock_history, mock_open):
    #     pass
