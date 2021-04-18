import csv
import math
import json
from enum import Enum
from collections import deque
from functools import reduce
from datetime import datetime, date


BTC_ORDERS_CSV = 'btc-orders.csv'
HISTORICAL_DATA = 'btc_by_date.json'


class Order:
    def __init__(self, currency, volume, date, type, price):
        self.currency = currency
        self.volume = volume
        self.date = date
        self.type = type
        self.price = price
        self.diff = 0

    @classmethod
    def init_class(cls, hist_data):
        with open(hist_data) as f:
            print('Loading BTC historical prices')
            cls.btc_by_date = json.load(f)

    @classmethod
    def from_row(cls, row, currency):
        volume = float(row['BTC Volume'])
        date = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S +0000')
        type = row['BTC Buy/Sell']
        if row['Ticker'] == 'BTC' and row['Currency'] == 'USD':
            price = float(row['Price'])
        else:
            price = cls.btc_by_date[date.strftime('%Y-%m-%d')]
        return cls(currency, volume, date, type, price)

    def __str__(self):
        return f'[{self.date}] - {self.type} {self.currency}: {self.volume} (diff: {self.diff})'


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
