from candles import get_candles
from config import DROP_RATE, MA_NEAR_PERCENT


def analyze(symbol, current_price):

    candle_list = get_candles(symbol)

    if len(candle_list) < 72:
        return None

    recent = candle_list[-72:]

    # 최근 6시간 최고 High
    high_index = max(
        range(len(recent)),
        key=lambda i: recent[i]["high"]
    )

    high_candle = recent[high_index]

    # 최고점 이후 캔들만 검사
    after = recent[high_index:]

    if len(after) < 2:
        return None

    low_candle = min(
        after,
        key=lambda x: x["low"]
    )

    high = high_candle["high"]
    low = low_candle["low"]

    drop = ((high - low) / high) * 100

    if drop < DROP_RATE:
        return None

    closes = [c["close"] for c in candle_list[-60:]]

    ma60 = sum(closes) / 60

    distance = abs(current_price - ma60) / ma60 * 100

    return {
        "symbol": symbol,

        "high": high,
        "low": low,

        "high_time": high_candle["time"],
        "low_time": low_candle["time"],

        "drop": drop,

        "ma60": ma60,

        "distance": distance,

        "near_ma": distance <= MA_NEAR_PERCENT
    }