class Form8949Row:
    """
    currency
    volume
    date_acquired
    date_sold
    proceeds
    cost_basis
    type
    gains
    """
    def __init__(self, currency, volume, date_acquired, date_sold, cost_basis,
                 proceeds, gains_type, gains):
        self.currency = currency
        self.volume = volume
        self.date_acquired = date_acquired
        self.date_sold = date_sold
        self.cost_basis = cost_basis
        self.proceeds = proceeds
        self.gains_type = gains_type
        self.gains = gains

    def __str__(self):
        return (f'Row:\n'
                f'- Prop:\t\t{self.volume} {self.currency}\n'
                f'- Acquired:\t{self.date_acquired}\n'
                f'- Sold:\t\t{self.date_sold}\n'
                f'- Cost Basis:\t{self.cost_basis}\n'
                f'- Proceeds:\t{self.proceeds}\n'
                f'- Time:\t\t{self.gains_type}\n'
                f'- Gains:\t{self.gains}')
