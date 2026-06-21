import time
from datetime import datetime

from scanner import get_top_futures
from candles import load_initial_candles, update_recent_candles
from websocket_client import start, resubscribe
from strategy import analyze
from price_manager import get_price
from state import watch_symbols, last_alert
from config import ALERT_COOLDOWN, REFRESH_HOURS
from notifier import send_alert


def refresh_watchlist():
    watch_symbols.clear()

    coins = get_top_futures()

    print("\n====== TOP30 ======\n")

    for i, coin in enumerate(coins, 1):
        symbol = coin["symbol"]
        watch_symbols.append(symbol)

        print(f"{i:2d}. {symbol:<20}{coin['gain']:.2f}%")

    print("\n공식 5분봉 다운로드...\n")

    success = 0

    for symbol in watch_symbols:
        if load_initial_candles(symbol):
            success += 1

    print(f"{success}/{len(watch_symbols)} 완료")


def update_candles_if_needed(last_update):
    now = datetime.now()

    if now.minute % 5 == 0 and now.second < 10:
        key = now.strftime("%Y-%m-%d %H:%M")

        if key != last_update:
            print("\n====== 5분봉 갱신 ======\n")

            success = 0

            for symbol in watch_symbols:
                if update_recent_candles(symbol):
                    success += 1

            print(f"5분봉 갱신 완료 {success}/{len(watch_symbols)}\n")

            return key

    return last_update


def update_top30_if_needed(last_refresh):
    now = datetime.now()

    if (
        now.hour in REFRESH_HOURS
        and now.minute == 0
        and now.second < 10
    ):
        key = now.strftime("%Y-%m-%d %H")

        if key != last_refresh:
            print("\n====== TOP30 자동 갱신 ======\n")

            refresh_watchlist()
            resubscribe()

            return key

    return last_refresh


def send_rebound_alert(symbol, price, result):
    message = (
        f"🚨 재반등 알림\n\n"
        f"코인 : {symbol}\n"
        f"현재가 : {price}\n"
        f"MA60 : {result['ma60']:.12g}\n"
        f"거리 : {result['distance']:.3f}%\n\n"
        f"고점 : {result['high']}\n"
        f"저점 : {result['low']}\n"
        f"하락률 : {result['drop']:.2f}%"
    )

    print("=" * 70)
    print(message)

    send_alert(message)


def monitor():
    last_candle_update = None
    last_top30_refresh = None

    while True:
        last_candle_update = update_candles_if_needed(last_candle_update)
        last_top30_refresh = update_top30_if_needed(last_top30_refresh)

        for symbol in watch_symbols:
            price = get_price(symbol)

            if price is None:
                continue

            result = analyze(symbol, price)

            if result is None:
                continue

            if not result["near_ma"]:
                continue

            now = time.time()
            last_time = last_alert.get(symbol, 0)

            if now - last_time < ALERT_COOLDOWN:
                continue

            last_alert[symbol] = now

            send_rebound_alert(symbol, price, result)

        time.sleep(15)


if __name__ == "__main__":
    refresh_watchlist()
    start()
    time.sleep(3)
    monitor()