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
def update_recent_candles(symbol):
    """
    최근 2개 공식 5분봉을 가져와서
    기존 마지막 봉은 교체하고,
    새 봉이 있으면 추가한다.
    항상 최근 72개만 유지한다.
    """

    url = f"{BASE_HTTP}/api/v1/contract/kline/{symbol}"

    params = {
        "interval": "Min5",
        "limit": 2
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

    count = min(len(times), len(opens), len(highs), len(lows), len(closes))

    if count == 0:
        return False

    new_candles = []

    for i in range(count):
        new_candles.append({
            "time": int(times[i]),
            "open": float(opens[i]),
            "high": float(highs[i]),
            "low": float(lows[i]),
            "close": float(closes[i]),
        })

    if symbol not in candles:
        candles[symbol] = []

    for new_candle in new_candles:
        replaced = False

        for idx, old_candle in enumerate(candles[symbol]):
            if old_candle["time"] == new_candle["time"]:
                candles[symbol][idx] = new_candle
                replaced = True
                break

        if not replaced:
            candles[symbol].append(new_candle)

    candles[symbol].sort(key=lambda x: x["time"])

    if len(candles[symbol]) > 72:
        candles[symbol] = candles[symbol][-72:]

    return True