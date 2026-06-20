import time

from scanner import get_top_futures
from candles import load_initial_candles
from websocket_client import start
from strategy import analyze
from price_manager import get_price
from state import watch_symbols


def refresh_watchlist():

    watch_symbols.clear()

    coins = get_top_futures()

    print("\n====== TOP30 ======\n")

    for i, coin in enumerate(coins, 1):

        symbol = coin["symbol"]

        watch_symbols.append(symbol)

        print(
            f"{i:2d}. "
            f"{symbol:<20}"
            f"{coin['gain']:.2f}%"
        )

    print("\n공식 5분봉 다운로드...\n")

    success = 0

    for symbol in watch_symbols:

        if load_initial_candles(symbol):
            success += 1

    print(f"{success}/{len(watch_symbols)} 완료")

    print("\nWebSocket 연결중...\n")


def monitor():

    while True:

        for symbol in watch_symbols:

            price = get_price(symbol)

            if price is None:
                continue

            result = analyze(symbol, price)

            if result is None:
                continue

            if result["near_ma"]:

                print("=" * 70)

                print(f"🚨 {symbol}")

                print(f"현재가 : {price}")

                print(f"MA60 : {result['ma60']:.6f}")

                print(f"거리 : {result['distance']:.3f}%")

                print(f"고점 : {result['high']}")

                print(f"저점 : {result['low']}")

                print(f"하락률 : {result['drop']:.2f}%")

        time.sleep(15)


if __name__ == "__main__":

    refresh_watchlist()

    start()

    time.sleep(3)

    monitor()