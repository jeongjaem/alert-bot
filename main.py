import requests
import time

BASE_URL = "https://api.mexc.com"


def get_symbols():
    """USDT 현물 코인 목록 가져오기"""
    url = f"{BASE_URL}/api/v3/exchangeInfo"

    data = requests.get(url, timeout=10).json()

    symbols = []

    for s in data["symbols"]:
        if (
            s["quoteAsset"] == "USDT"
            and s["status"] == "ENABLED"
        ):
            symbols.append(s["symbol"])

    return symbols


def get_klines(symbol):
    """
    최근 6시간(72개 5분봉)
    """

    url = f"{BASE_URL}/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 73
    }

    r = requests.get(url, params=params, timeout=10)

    return r.json()


def calc_gain(candles):
    """
    최근 6시간 상승률
    """

    if len(candles) < 73:
        return None

    start = float(candles[0][4])
    end = float(candles[-1][4])

    if start == 0:
        return None

    return ((end - start) / start) * 100


def scan_top30():

    symbols = get_symbols()

    result = []

    total = len(symbols)

    print(f"총 {total}개 코인 스캔 시작\n")

    for idx, symbol in enumerate(symbols):

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

        print(f"{idx+1}/{total} 완료", end="\r")

        time.sleep(0.05)

    result.sort(
        key=lambda x: x["gain"],
        reverse=True
    )

    return result[:30]


if __name__ == "__main__":

    top30 = scan_top30()

    print("\n\n====== 최근 6시간 상승률 TOP30 ======\n")

    for i, coin in enumerate(top30, 1):

        print(
            f"{i:2d}. "
            f"{coin['symbol']:<15}"
            f"{coin['gain']:.2f}%"
        )