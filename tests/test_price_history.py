from datetime import datetime
import mock
import pytest

from price_history import PriceHistory, ONE_HOUR, ONE_DAY


class TestingPriceHistory(PriceHistory):
    def __init__(self, interval):
        self.history_dict = {}
        self.date_format = self._date_format_for_interval(interval)


# # @mock.patch('builtins.open')
# # @mock.patch('price_history.HistoricalData')
# class TestGetItem:
#     def test_field_dict_is_queried_with_proper_date_format(self):
#         ph = TestingPriceHistory()
#         # How would I idiomatically test that it uses the proper
#         # date format without tying the test too much to implementation?
#         ph.history_dict[]

#         pass


@mock.patch('price_history.HistoricalData')
class TestSetItem:
    def test_field_dict_stores_price_with_proper_date_format(self, mock_history):
        # I think I'll just mock out _get_history
        pass


class TestGetSet:
    def test_getting_set_items_matches_for_rounded_dates_with_day_interval(self):
        ph = TestingPriceHistory(ONE_DAY)
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

    def test_getting_set_items_matches_for_rounded_dates_with_hour_interval(self):
        pass


@mock.patch('price_history.HistoricalData')
class TestInit:
    def test_raise_error_with_unsupported_interval(self, mock_history):
        with pytest.raises(Exception):
            PriceHistory('BTC-USD', 1234)

    def test_use_file_history_if_exists(self, mock_history):
        pass

    def test_use_crypto_data_api_if_file_dne(self, mock_history):
        pass

    def test_saves_file_after_crypto_api(self, mock_history):
        pass

    def test_dict_keys_use_one_day_format(self, mock_history):
        pass

    def test_dict_keys_use_one_hour_format(self, mock_history):
        pass
