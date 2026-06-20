import time
from datetime import datetime

from scanner import get_top_futures
from candles import load_initial_candles, update_recent_candles
from websocket_client import start
from strategy import analyze
from price_manager import get_price
from state import watch_symbols, last_alert
from config import ALERT_COOLDOWN


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
    print("\nWebSocket 연결중...\n")


def update_candles_if_needed(last_candle_update):
    now = datetime.now()

    if now.minute % 5 == 0 and now.second < 10:
        key = now.strftime("%Y-%m-%d %H:%M")

        if last_candle_update != key:
            print("\n5분봉 갱신 중...")

            success = 0

            for symbol in watch_symbols:
                if update_recent_candles(symbol):
                    success += 1

            print(f"5분봉 갱신 완료: {success}/{len(watch_symbols)}\n")

            return key

    return last_candle_update


def monitor():
    last_candle_update = None

    while True:
        last_candle_update = update_candles_if_needed(last_candle_update)

        for symbol in watch_symbols:
            price = get_price(symbol)

            if price is None:
                continue

            result = analyze(symbol, price)

            if result is None:
                continue

            if result["near_ma"]:
                now = time.time()

                if symbol in last_alert:
                    if now - last_alert[symbol] < ALERT_COOLDOWN:
                        continue

                last_alert[symbol] = now

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