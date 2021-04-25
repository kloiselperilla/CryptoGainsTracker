import csv
import math
import json
from enum import Enum
from collections import deque
from functools import reduce
from datetime import datetime, date
from Historic_Crypto import HistoricalData

from form_8949_row import Form8949Row
from order import Order
from price_history import PriceHistory

BTC_ORDERS_CSV = 'btc-orders.csv'
HISTORICAL_DATA = 'btc_by_date.json'


def populate_historical_data(interval, start='2017-01-01-00-00'):
    # new = HistoricalData('BTC-USD',86400,'2017-01-01-00-00').retrieve_data()
    new = HistoricalData('BTC-USD', interval, '2017-01-01-00-00').retrieve_data()
    pass


def calculate_gains(buy, sell, gains_dict, diff=0, verbose=False):
    def addYears(d, years):
        try:
            # Return same day of the current year
            return d.replace(year=d.year + years)
        except ValueError:
            # If not same day, it will return other, i.e.  February 29 to March 1 etc.
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
    if diff:
        if buy.diff:
            print()
            print()
            print('LOOK HERE: diff from split and also existing volume used up on buy')
            print()
            print()
        volume_in_sale = diff - buy.diff
        buy.diff += diff
    else:
        volume_in_sale = buy.volume - buy.diff
    buy_worth = volume_in_sale * buy.price
    sell_worth = volume_in_sale * sell.price
    gain = sell_worth - buy_worth
    long = sell.date > addYears(buy.date, 1)
    if verbose:
        print('Volume in sale:', volume_in_sale)
        print(f'Sold {sell} from {buy}: gains = {gain}')
    if long:
        gains_dict['long'] += gain
    else:
        gains_dict['short'] += gain


def process_orders(orders):
    earlier = 0
    later = 0
    diff = 0
    capital_gains = {
        'long': 0,
        'short': 0,
    }
    while later < len(orders):
        if orders[later].type == 'SELL':
            amt_sold = orders[later].volume
            match_bought_accum = 0
            while earlier < later and match_bought_accum < amt_sold:
                if orders[earlier].type == 'BUY':
                    current_bought = orders[earlier].volume - orders[earlier].diff
                    if match_bought_accum + current_bought > amt_sold:
                        diff = amt_sold - match_bought_accum
                        calculate_gains(orders[earlier], orders[later], capital_gains, diff)
                        break
                    else:
                        match_bought_accum += current_bought
                        calculate_gains(orders[earlier], orders[later], capital_gains)
                earlier += 1
        later += 1
    return capital_gains


if __name__ == "__main__":
    Order.init_class(HISTORICAL_DATA)
    orders = []
    with open(BTC_ORDERS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(Order.from_row(row, 'BTC'))
    print(process_orders(orders))
