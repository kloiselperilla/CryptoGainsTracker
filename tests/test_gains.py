from datetime import datetime

from gains import add_year


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


class TestCalculateGains:
    pass
