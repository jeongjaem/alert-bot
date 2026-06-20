import requests
import time

BASE_URL = "https://api.mexc.com"


def get_symbols():
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    data = requests.get(url, timeout=15).json()

    symbols = []

    for s in data.get("symbols", []):
        symbol = s.get("symbol", "")

        if symbol.endswith("USDT"):
            symbols.append(symbol)

    return symbols


def get_klines(symbol):
    url = f"{BASE_URL}/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 73
    }

    data = requests.get(url, params=params, timeout=15).json()
    return data


def calc_gain(candles):
    if not isinstance(candles, list):
        return None

    if len(candles) < 73:
        return None

    start_price = float(candles[0][4])
    end_price = float(candles[-1][4])

    if start_price <= 0:
        return None

    return ((end_price - start_price) / start_price) * 100


def scan_top30():
    symbols = get_symbols()
    result = []

    print(f"총 {len(symbols)}개 코인 스캔 시작\n")

    for idx, symbol in enumerate(symbols, 1):
        try:
            candles = get_klines(symbol)
            gain = calc_gain(candles)

            if gain is not None:
                result.append({
                    "symbol": symbol,
                    "gain": gain
                })

        except Exception:
            pass

        print(f"{idx}/{len(symbols)} 완료", end="\r")
        time.sleep(0.05)

    result.sort(key=lambda x: x["gain"], reverse=True)

    return result[:30]


if __name__ == "__main__":
    top30 = scan_top30()

    print("\n\n====== 최근 6시간 상승률 TOP30 ======\n")

    for i, coin in enumerate(top30, 1):
        print(f"{i:2d}. {coin['symbol']:<15} {coin['gain']:.2f}%")