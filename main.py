import requests
import time

BASE_URL = "https://contract.mexc.com"


def get_top30_futures():
    url = f"{BASE_URL}/api/v1/contract/ticker"
    data = requests.get(url, timeout=15).json()

    tickers = data.get("data", [])

    result = []

    for t in tickers:
        symbol = t.get("symbol", "")

        if not symbol.endswith("_USDT"):
            continue

        rise_fall_rate = t.get("riseFallRate", 0)

        try:
            gain = float(rise_fall_rate) * 100
        except:
            continue

        result.append({
            "symbol": symbol,
            "gain": gain,
            "last_price": t.get("lastPrice")
        })

    result.sort(key=lambda x: x["gain"], reverse=True)

    return result[:30]


if __name__ == "__main__":
    top30 = get_top30_futures()

    print("\n====== MEXC 선물 상승률 TOP30 ======\n")

    for i, coin in enumerate(top30, 1):
        print(
            f"{i:2d}. {coin['symbol']:<20} "
            f"{coin['gain']:.2f}% "
            f"현재가: {coin['last_price']}"
        )