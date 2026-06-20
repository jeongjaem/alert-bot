import requests

from config import BASE_HTTP

# symbol -> 최근 72개 캔들
candles = {}


def load_initial_candles(symbol):
    """
    프로그램 시작 시
    최근 72개 5분봉 다운로드
    """

    url = f"{BASE_HTTP}/api/v1/contract/kline/{symbol}"

    params = {
        "interval": "Min5",
        "limit": 72
    }

    r = requests.get(url, params=params, timeout=15).json()

    if not r.get("success"):
        return False

    d = r["data"]

    result = []

    for i in range(len(d["time"])):

        result.append({
            "time": d["time"][i],
            "open": float(d["open"][i]),
            "high": float(d["high"][i]),
            "low": float(d["low"][i]),
            "close": float(d["close"][i]),
        })

    candles[symbol] = result

    return True


def get_candles(symbol):

    return candles.get(symbol, [])


def update_last_candle(symbol):
    """
    최신 5분봉 하나만 갱신
    """

    url = f"{BASE_HTTP}/api/v1/contract/kline/{symbol}"

    params = {
        "interval": "Min5",
        "limit": 1
    }

    r = requests.get(url, params=params, timeout=15).json()

    if not r.get("success"):
        return

    d = r["data"]

    candle = {
        "time": d["time"][0],
        "open": float(d["open"][0]),
        "high": float(d["high"][0]),
        "low": float(d["low"][0]),
        "close": float(d["close"][0]),
    }

    if symbol not in candles:
        candles[symbol] = [candle]
        return

    # 같은 캔들이면 교체
    if candles[symbol][-1]["time"] == candle["time"]:
        candles[symbol][-1] = candle

    else:
        candles[symbol].append(candle)

        if len(candles[symbol]) > 72:
            candles[symbol].pop(0)