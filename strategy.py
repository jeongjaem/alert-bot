from candles import get_candles


def get_signal(symbol, current_price):

    candle_list = get_candles(symbol)

    if len(candle_list) < 60:
        return None

    # 최근 72개(6시간)
    recent = candle_list[-72:]

    highest = max(recent, key=lambda x: x["high"])
    lowest = min(recent, key=lambda x: x["low"])

    high_price = highest["high"]
    low_price = lowest["low"]

    if high_price <= 0:
        return None

    # 고점 대비 하락률
    drop = ((high_price - low_price) / high_price) * 100

    # 저점이 고점보다 늦게 나왔는지
    low_after_high = lowest["time"] > highest["time"]

    # MA60
    closes = [c["close"] for c in candle_list[-60:]]
    ma60 = sum(closes) / 60

    # 현재가와 MA60 거리
    distance = abs(current_price - ma60) / ma60 * 100

    return {
        "drop": drop,
        "low_after_high": low_after_high,
        "ma60": ma60,
        "distance": distance,
        "high": high_price,
        "low": low_price,
        "high_time": highest["time"],
        "low_time": lowest["time"],
    }