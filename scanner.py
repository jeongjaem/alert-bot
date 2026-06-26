import requests

from config import BASE_HTTP


MIN_VOLUME = 1_000_000


def get_top_futures():

    url = f"{BASE_HTTP}/api/v1/contract/ticker"

    try:
        data = requests.get(url, timeout=15).json()
    except Exception:
        return []

    result = []

    for coin in data.get("data", []):

        symbol = coin.get("symbol", "")

        if not symbol.endswith("_USDT"):
            continue

        if "riseFallRate" not in coin:
            continue

        if "lastPrice" not in coin:
            continue

        try:
            gain = float(coin["riseFallRate"]) * 100
            last_price = float(coin["lastPrice"])

            # 24시간 거래대금(USDT)
            volume = float(coin.get("amount24", 0))

        except Exception:
            continue

        if volume < MIN_VOLUME:
            continue

        result.append({
            "symbol": symbol,
            "gain": gain,
            "last_price": last_price,
            "volume": volume,
        })

    print(f"\n거래량 1M 이상 : {len(result)}개")

    return result