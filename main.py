from websocket_client import start
from state import latest_price
import time
from scanner import get_top_futures
from state import watch_symbols


def refresh_watchlist():

    coins = get_top_futures()

    watch_symbols.clear()

    print("\n====== TOP30 ======\n")

    for i, coin in enumerate(coins, 1):

        watch_symbols.append(coin["symbol"])

        print(
            f"{i:2d}. "
            f"{coin['symbol']:<20}"
            f"{coin['gain']:.2f}%"
        )

    print("\n감시 대상 :", len(watch_symbols))


if __name__ == "__main__":

    refresh_watchlist()   # TOP30 가져오기

    start()               # WebSocket 시작

    while True:

        print("-------------------------")

        for symbol in watch_symbols[:5]:

            if symbol in latest_price:
                print(symbol, latest_price[symbol])

        time.sleep(5)