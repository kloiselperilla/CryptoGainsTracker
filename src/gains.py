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


def add_year(d):
    """
        Add amount of time for long-term capital gains
        according to https://www.naspp.com/Blog/March-2016/Tax-Holding-Periods-and-Leap-Year
    """
    if d.month == 2 and d.day >= 28:
        return d.replace(year=d.year + 1, month=3, day=1, hour=0, minute=0, second=0)
    else:
        return d.replace(year=d.year + 1, hour=0, minute=0, second=0) + timedelta(days=1)


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


def form_rows_to_csv(form_rows: list[Form8949Row], timeframe=None):
    fieldnames = ['Asset', 'Volume', 'Date Acquired', 'Date Sold', 'Cost Basis',
                  'Proceeds', 'Gains']
    if not timeframe:
        fieldnames.append('Gains Timeframe')
        csv_file_name = 'btc_gains_all.csv'
    else:
        csv_file_name = 'btc_gains_{timeframe}.csv'

    with open(csv_file_name, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for r in form_rows:
            if not timeframe or timeframe == r.gains_type:
                write_row_dict = {
                    'Asset': r.currency,
                    'Volume': r.volume,
                    'Date Acquired': r.date_acquired,
                    'Date Sold': r.date_sold,
                    'Cost Basis': r.cost_basis,
                    'Proceeds': r.proceeds,
                    'Gains': r.gains,
                }
                if not timeframe:
                    write_row_dict['Gains Timeframe'] = r.gains_type
                writer.writerow(write_row_dict)


if __name__ == "__main__":
    ph = PriceHistory('BTC-USD', ONE_HOUR)
    orders = []
    with open(BTC_ORDERS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(Order.from_row(row, 'BTC', ph))
    form_rows = populate_form_8949_rows(orders)
    form_rows_to_csv(form_rows)

# TODO: Try out with more data to see if long-terms kick in
# TODO: Generalize currency code to use more than BTC
# TODO: Get individual gains tables for each crypto
# TODO (stretch): Allow for passing in all trades and spitting out all gains
#   This would require counting a crypto-crypto as a buy for one and a sell for the other at once
