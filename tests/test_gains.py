from datetime import datetime

from gains import add_year


class TestAddYears:
    def test_regular_day_same_day_year_later_next_day(self):
        buy_date = datetime.strptime('2018-06-15 00:00:00', '%Y-%m-%d %H:%M:%S')

        year_later = add_year(buy_date)

        assert year_later.strftime('%Y-%m-%d') == '2019-06-16'

    def test_feb_28_before_leap_returns_mar_1(self):
        buy_date = datetime.strptime('2019-02-28 00:00:00', '%Y-%m-%d %H:%M:%S')

        year_later = add_year(buy_date)

        assert year_later.strftime('%Y-%m-%d') == '2020-03-01'

    def test_feb_28_29_on_leap_returns_mar_1(self):
        buy_date_a = datetime.strptime('2020-02-28 00:00:00', '%Y-%m-%d %H:%M:%S')
        buy_date_b = datetime.strptime('2020-02-29 00:00:00', '%Y-%m-%d %H:%M:%S')

        year_later_a = add_year(buy_date_a)
        year_later_b = add_year(buy_date_b)

        assert year_later_a.strftime('%Y-%m-%d') == '2021-03-01'
        assert year_later_b.strftime('%Y-%m-%d') == '2021-03-01'

    def test_nye_returns_new_years_2_years_forward(self):
        buy_date = datetime.strptime('2018-12-31 00:00:00', '%Y-%m-%d %H:%M:%S')

        year_later = add_year(buy_date)

        assert year_later.strftime('%Y-%m-%d') == '2020-01-01'


class TestCalculateGains:
    pass
