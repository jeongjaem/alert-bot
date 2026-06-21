import requests

from config import BASE_HTTP, TOP_COUNT


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

        # 선물 티커에 필수로 있어야 하는 값
        if "riseFallRate" not in coin:
            continue

        if "lastPrice" not in coin:
            continue

        try:
            gain = float(coin["riseFallRate"]) * 100
            last_price = float(coin["lastPrice"])
        except Exception:
            continue

        result.append({
            "symbol": symbol,
            "gain": gain,
            "last_price": last_price,
        })

    result.sort(
        key=lambda x: x["gain"],
        reverse=True
    )

    return result[:TOP_COUNT]