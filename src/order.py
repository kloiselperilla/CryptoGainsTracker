from datetime import datetime

from price_history import PriceHistory


class Order:
    def __init__(self, currency, volume: float, date: datetime, ord_type, price: float):
        self.currency = currency
        self.volume = volume
        self.date = date
        self.sells = []
        # self.proceeds = None
        self.type = ord_type
        self.price = price
        self.used_up = 0

    @property
    def cost_basis(self):
        return self.volume * self.price

    @classmethod
    def from_row(cls, row, currency, price_hist: PriceHistory):
        volume = float(row['BTC Volume'])
        date = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S +0000')
        type = row['BTC Buy/Sell']
        if row['Ticker'] == 'BTC' and row['Currency'] == 'USD':
            price = float(row['Price'])
        else:
            # price = price_hist[date.strftime('%Y-%m-%d')]
            price = price_hist[date]
        return cls(currency, volume, date, type, price)

    def __str__(self):
        return f'[{self.date}] - {self.type} {self.currency}: {self.volume} (used up: {self.used_up})'
