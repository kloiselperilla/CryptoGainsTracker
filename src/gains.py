import csv

BTC_ORDERS_CSV = 'btc-orders.csv'

with open(BTC_ORDERS_CSV, newline="") as f:
    reader = csv.DictReader(f)

