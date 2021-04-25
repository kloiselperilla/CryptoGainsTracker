class Order:
    def __init__(self, currency, volume, date, type, price):
        self.currency = currency
        self.volume = volume
        self.date = date
        self.sells = []
        # self.proceeds = None
        self.type = type
        self.price = price
        self.diff = 0

    @property
    def cost_basis(self):
        return self.volume * self.price

    @classmethod
    def init_class(cls, hist_data):
        with open(hist_data) as f:
            print('Loading BTC historical prices')
            if
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
