import csv
import math
import json
from calendar import monthrange
from enum import Enum
from collections import deque
from functools import reduce
from datetime import datetime, date, timedelta
from Historic_Crypto import HistoricalData

from form_8949_row import Form8949Row
from order import Order
from price_history import PriceHistory, ONE_HOUR

BTC_ORDERS_CSV = 'btc-orders.csv'
# HISTORICAL_DATA = 'btc_by_date.json'


# def populate_historical_data(interval, start='2017-01-01-00-00'):
#     # new = HistoricalData('BTC-USD',86400,'2017-01-01-00-00').retrieve_data()
#     new = HistoricalData('BTC-USD', interval, '2017-01-01-00-00').retrieve_data()
#     pass


def add_year(d):
    """
        Add amount of time for long-term capital gains
        according to https://www.naspp.com/Blog/March-2016/Tax-Holding-Periods-and-Leap-Year
    """
    if d.month == 2 and d.day >= 28:
        return d.replace(year=d.year + 1, month=3, day=1, hour=0, minute=0, second=0)
    else:
        return d.replace(year=d.year + 1, hour=0, minute=0, second=0) + timedelta(days=1)


# def calculate_gains(buy, sell, gains_dict, diff=0, verbose=False):
#     if diff:
#         volume_in_sale = diff
#         buy.used_up += diff
#     else:
#         volume_in_sale = buy.volume - buy.used_up
#     buy_worth = volume_in_sale * buy.price
#     sell_worth = volume_in_sale * sell.price
#     gain = sell_worth - buy_worth
#     long_term = sell.date >= add_year(buy.date)
#     if verbose:
#         print('Volume in sale:', volume_in_sale)
#         print(f'Sold {sell} from {buy}: gains = {gain}')
#     if long_term:
#         gains_dict['long'] += gain
#     else:
#         gains_dict['short'] += gain


def calculate_row(buy, sell, gains_dict, diff=0, verbose=False):
    if verbose:
        print(f'Selling {sell} from {buy}; diff: {diff}')
    if diff:
        volume_in_sale = diff
        buy.used_up += diff
        if verbose:
            print(f'Setting buy used_up to {buy.used_up}')
    else:
        volume_in_sale = buy.volume - buy.used_up
    buy_worth = volume_in_sale * buy.price
    sell_worth = volume_in_sale * sell.price
    gain = sell_worth - buy_worth
    long_term = sell.date >= add_year(buy.date)
    if verbose:
        print('Volume in sale:', volume_in_sale)
        print(f'Sold {sell} from {buy}: gains = {gain}')
    if long_term:
        gains_type = 'long'
    else:
        gains_type = 'short'
    row = Form8949Row('BTC', volume_in_sale, buy.date, sell.date, buy_worth,
                      sell_worth, gains_type, gain)
    return row


# def process_orders(orders):
#     earlier = 0
#     later = 0
#     diff = 0
#     capital_gains = {
#         'long': 0,
#         'short': 0,
#     }
#     while later < len(orders):
#         if orders[later].type == 'SELL':
#             amt_sold = orders[later].volume
#             match_bought_accum = 0
#             while earlier < later and match_bought_accum < amt_sold:
#                 if orders[earlier].type == 'BUY':
#                     current_bought = orders[earlier].volume - orders[earlier].diff
#                     if match_bought_accum + current_bought > amt_sold:
#                         diff = amt_sold - match_bought_accum
#                         calculate_gains(orders[earlier], orders[later], capital_gains, diff)
#                         break
#                     else:
#                         match_bought_accum += current_bought
#                         calculate_gains(orders[earlier], orders[later], capital_gains)
#                 earlier += 1
#         later += 1
#     return capital_gains


def populate_form_8949_rows(orders, verbose=False):
    earlier = 0
    later = 0
    diff = 0
    capital_gains = {
        'long': 0,
        'short': 0,
    }
    rows = []
    while later < len(orders):
        if orders[later].type == 'SELL':
            # When you sell, you either have:
            #   - Equal volume to a corresponding buy
            #   - A smaller sell than a previous buy, splitting the buy in the form
            #     - The difference for that buy gets checked for the next sell
            #   - A smaller buy than the sell, splitting the sell over multiple buys
            #     - Check that difference and start this check again
            amt_sold = orders[later].volume
            match_bought_accum = 0
            # float-friendly <=
            while not math.isclose(match_bought_accum, amt_sold) and match_bought_accum < amt_sold:
                if orders[earlier].type == 'BUY':
                    if earlier >= later:
                        raise Exception('Invalid Data: Sold more than bought')
                    # Fill out a row
                    current_bought = orders[earlier].volume - orders[earlier].used_up
                    if match_bought_accum + current_bought > amt_sold:
                        # Buy needs to be split
                        # diff is the how much of the buy is being split off for a too-small sell
                        diff = amt_sold - match_bought_accum
                        rows.append(calculate_row(orders[earlier], orders[later], capital_gains, diff, verbose=verbose))
                        if math.isclose(orders[earlier].used_up, orders[earlier].volume):
                            earlier += 1
                        break
                    else:
                        match_bought_accum += current_bought
                        rows.append(calculate_row(orders[earlier], orders[later], capital_gains, verbose=verbose))
                earlier += 1
        later += 1
    return rows


if __name__ == "__main__":
    # Order.init_class(HISTORICAL_DATA)
    ph = PriceHistory('BTC-USD', ONE_HOUR)
    orders = []
    with open(BTC_ORDERS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(Order.from_row(row, 'BTC'))
    print(process_orders(orders))
    form_rows = populate_form_8949_rows(orders)
