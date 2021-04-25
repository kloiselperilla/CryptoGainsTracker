from datetime import datetime
import pytest
import math

from gains import add_year, populate_form_8949_rows
from order import Order


class TestAddYear:
    def test_regular_day_same_day_year_later_next_day_at_midnight(self):
        buy_date = datetime.strptime('2018-06-15 00:00:00', '%Y-%m-%d %H:%M:%S')

        year_later = add_year(buy_date)

        assert year_later.strftime('%Y-%m-%d %H:%M:%S') == '2019-06-16 00:00:00'

    def test_feb_28_before_leap_returns_mar_1(self):
        buy_date = datetime.strptime('2019-02-28 01:23:45', '%Y-%m-%d %H:%M:%S')

        year_later = add_year(buy_date)

        assert year_later.strftime('%Y-%m-%d %H:%M:%S') == '2020-03-01 00:00:00'

    def test_feb_28_29_on_leap_returns_mar_1(self):
        buy_date_a = datetime.strptime('2020-02-28 01:23:45', '%Y-%m-%d %H:%M:%S')
        buy_date_b = datetime.strptime('2020-02-29 05:56:43', '%Y-%m-%d %H:%M:%S')

        year_later_a = add_year(buy_date_a)
        year_later_b = add_year(buy_date_b)

        assert year_later_a.strftime('%Y-%m-%d %H:%M:%S') == '2021-03-01 00:00:00'
        assert year_later_b.strftime('%Y-%m-%d %H:%M:%S') == '2021-03-01 00:00:00'

    def test_nye_returns_new_years_2_years_forward(self):
        buy_date = datetime.strptime('2018-12-31 02:34:56', '%Y-%m-%d %H:%M:%S')

        year_later = add_year(buy_date)

        assert year_later.strftime('%Y-%m-%d %H:%M:%S') == '2020-01-01 00:00:00'


class TestPopulateForm8949Rows:
    def test_equal_buy_and_sell_dont_split(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_4 = datetime.strptime('2018-04-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 1.0, date_1, 'BUY', 1000.0)
        sell_a = Order('BTC', 1.0, date_2, 'SELL', 2000.0)
        buy_b = Order('BTC', 2.0, date_3, 'BUY', 3000.0)
        sell_b = Order('BTC', 2.0, date_4, 'SELL', 1500.0)
        ords = [buy_a, sell_a, buy_b, sell_b]

        rows = populate_form_8949_rows(ords)

        assert math.isclose(rows[0].volume, 1.0)
        assert rows[0].date_acquired == date_1
        assert rows[0].date_sold == date_2
        assert math.isclose(rows[0].cost_basis, 1000.0)
        assert math.isclose(rows[0].proceeds, 2000.0)
        assert math.isclose(rows[0].gains, 1000.0)

        assert math.isclose(rows[1].volume, 2.0)
        assert rows[1].date_acquired == date_3
        assert rows[1].date_sold == date_4
        assert math.isclose(rows[1].cost_basis, 6000.0)
        assert math.isclose(rows[1].proceeds, 3000.0)
        assert math.isclose(rows[1].gains, -3000.0)

    def test_bigger_buy_than_sell_splits_sell(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 1.0, date_1, 'BUY', 1000.0)
        sell_a = Order('BTC', 0.5, date_2, 'SELL', 3000.0)
        sell_b = Order('BTC', 0.5, date_3, 'SELL', 2000.0)
        ords = [buy_a, sell_a, sell_b]

        rows = populate_form_8949_rows(ords)

        assert math.isclose(rows[0].volume, 0.5)
        assert rows[0].date_acquired == date_1
        assert rows[0].date_sold == date_2
        assert math.isclose(rows[0].cost_basis, 500.0)
        assert math.isclose(rows[0].proceeds, 1500.0)
        assert math.isclose(rows[0].gains, 1000.0)

        assert math.isclose(rows[1].volume, 0.5)
        assert rows[1].date_acquired == date_1
        assert rows[1].date_sold == date_3
        assert math.isclose(rows[1].cost_basis, 500.0)
        assert math.isclose(rows[1].proceeds, 1000.0)
        assert math.isclose(rows[1].gains, 500.0)

    def test_bigger_sell_than_buy_splits_buy(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 0.25, date_1, 'BUY', 1000.0)
        buy_b = Order('BTC', 0.75, date_2, 'BUY', 100.0)
        sell_a = Order('BTC', 1.0, date_3, 'SELL', 2000.0)
        ords = [buy_a, buy_b, sell_a]

        rows = populate_form_8949_rows(ords)

        assert math.isclose(rows[0].volume, 0.25)
        assert rows[0].date_acquired == date_1
        assert rows[0].date_sold == date_3
        assert math.isclose(rows[0].cost_basis, 250.0)
        assert math.isclose(rows[0].proceeds, 500.0)
        assert math.isclose(rows[0].gains, 250.0)

        assert math.isclose(rows[1].volume, 0.75)
        assert rows[1].date_acquired == date_2
        assert rows[1].date_sold == date_3
        assert math.isclose(rows[1].cost_basis, 75.0)
        assert math.isclose(rows[1].proceeds, 1500.0)
        assert math.isclose(rows[1].gains, 1425.0)

    def test_raise_error_when_sold_more_than_bought(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 0.25, date_1, 'BUY', 1000.0)
        sell_a = Order('BTC', 1.0, date_2, 'SELL', 2000.0)
        ords = [buy_a, sell_a]

        with pytest.raises(Exception):
            populate_form_8949_rows(ords)

    def test_raise_error_when_sell_before_buy(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        sell_a = Order('BTC', 1.0, date_1, 'SELL', 2000.0)
        ords = [sell_a]

        with pytest.raises(Exception):
            populate_form_8949_rows(ords)

    def test_ignore_buys_without_a_sell(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 0.5, date_1, 'BUY', 1000.0)
        buy_b = Order('BTC', 2.0, date_2, 'BUY', 4000.0)
        sell_a = Order('BTC', 1.0, date_3, 'SELL', 2000.0)
        ords = [buy_a, buy_b, sell_a]

        rows = populate_form_8949_rows(ords)

        assert math.isclose(rows[0].gains, 500.0)
        assert math.isclose(rows[1].gains, -1000.0)
        assert len(rows) == 2

    def test_includes_both_long_and_short_term(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_4 = datetime.strptime('2019-04-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 1.0, date_1, 'BUY', 1000.0)
        sell_a = Order('BTC', 1.0, date_2, 'SELL', 2000.0)
        buy_b = Order('BTC', 2.0, date_3, 'BUY', 3000.0)
        sell_b = Order('BTC', 2.0, date_4, 'SELL', 1500.0)
        ords = [buy_a, sell_a, buy_b, sell_b]

        rows = populate_form_8949_rows(ords)

        assert math.isclose(rows[0].gains, 1000.0)
        assert rows[0].gains_type == 'short'

        assert math.isclose(rows[1].gains, -3000.0)
        assert rows[1].gains_type == 'long'

    def test_sell_can_handle_multiple_small_buys(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_4 = datetime.strptime('2018-04-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 0.2, date_1, 'BUY', 1000.0)
        buy_b = Order('BTC', 0.4, date_2, 'BUY', 2000.0)
        buy_c = Order('BTC', 0.6, date_3, 'BUY', 3000.0)
        sell_a = Order('BTC', 1.2, date_4, 'SELL', 6000.0)
        ords = [buy_a, buy_b, buy_c, sell_a]

        rows = populate_form_8949_rows(ords)

        assert math.isclose(rows[0].gains, 1000.0)
        assert math.isclose(rows[1].gains, 1600.0)
        assert math.isclose(rows[2].gains, 1800.0)

    def test_buy_can_handle_multiple_small_sells(self):
        date_1 = datetime.strptime('2018-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_2 = datetime.strptime('2018-02-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_3 = datetime.strptime('2018-03-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        date_4 = datetime.strptime('2018-04-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        buy_a = Order('BTC', 0.05, date_1, 'BUY', 500.0)
        buy_b = Order('BTC', 0.95, date_1, 'BUY', 1000.0)
        sell_a = Order('BTC', 0.2, date_2, 'SELL', 2000.0)
        sell_b = Order('BTC', 0.3, date_3, 'SELL', 3000.0)
        sell_c = Order('BTC', 0.5, date_4, 'SELL', 6000.0)
        ords = [buy_a, buy_b, sell_a, sell_b, sell_c]

        rows = populate_form_8949_rows(ords)

        # The first 0.05
        assert math.isclose(rows[0].gains, 75.0)
        # The remainder of 0.2 sell: 0.15
        assert math.isclose(rows[1].gains, 150.0)
        # Entirety of 0.3 sell
        assert math.isclose(rows[2].gains, 600.0)
        # Entirety of 0.5 sell
        assert math.isclose(rows[3].gains, 2500.0)
