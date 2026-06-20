import requests
from config import BASE_HTTP, TOP_COUNT


def get_top_futures():

    url = f"{BASE_HTTP}/api/v1/contract/ticker"

    data = requests.get(url, timeout=15).json()

    result = []

    for coin in data.get("data", []):

        symbol = coin.get("symbol", "")

        if not symbol.endswith("_USDT"):
            continue

        try:
            gain = float(coin["riseFallRate"]) * 100
            last_price = float(coin["lastPrice"])
        except:
            continue

        result.append({
            "symbol": symbol,
            "gain": gain,
            "last_price": last_price
        })

    result.sort(
        key=lambda x: x["gain"],
        reverse=True
    )

    return result[:TOP_COUNT]