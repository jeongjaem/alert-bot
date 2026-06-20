import requests

from config import BASE_HTTP

candles = {}


def load_initial_candles(symbol):

    url = f"{BASE_HTTP}/api/v1/contract/kline/{symbol}"

    params = {
        "interval": "Min5",
        "limit": 72
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

    except Exception:
        return False

    if not data.get("success"):
        return False

    d = data.get("data", {})

    times = d.get("time", [])
    opens = d.get("open", [])
    highs = d.get("high", [])
    lows = d.get("low", [])
    closes = d.get("close", [])

    count = min(
        len(times),
        len(opens),
        len(highs),
        len(lows),
        len(closes)
    )

    if count == 0:
        return False

    result = []

    for i in range(count):

        result.append({
            "time": int(times[i]),
            "open": float(opens[i]),
            "high": float(highs[i]),
            "low": float(lows[i]),
            "close": float(closes[i]),
        })

    candles[symbol] = result

    return True


def get_candles(symbol):
    return candles.get(symbol, [])