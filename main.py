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

    refresh_watchlist()