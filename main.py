import time

from scanner import get_top_futures
from websocket_client import start

from state import watch_symbols

from candles import load_initial_candles

from strategy import analyze

from price_manager import get_price


def refresh_watchlist():

    coins = get_top_futures()

    watch_symbols.clear()

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

    print("\n감시 시작\n")


if __name__ == "__main__":

    refresh_watchlist()

    start()

    while True:

        for symbol in watch_symbols:

            price = get_price(symbol)

            if price is None:
                continue

            result = analyze(symbol, price)

            if result is None:
                continue

            if result["near_ma"]:

                print("=" * 60)

                print(f"🚨 {symbol}")

                print(f"현재가 : {price}")

                print(f"MA60 : {result['ma60']:.6f}")

                print(f"거리 : {result['distance']:.3f}%")

                print(f"고점 : {result['high']}")

                print(f"저점 : {result['low']}")

                print(f"하락률 : {result['drop']:.2f}%")

        time.sleep(15)