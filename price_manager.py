current_price = {}


def update_price(symbol, price):
    current_price[symbol] = float(price)


def get_price(symbol):
    return current_price.get(symbol)


def has_price(symbol):
    return symbol in current_price