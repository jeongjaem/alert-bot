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

    print("\n====== 거래량 1M 이상 선물 코인 ======\n")
    print(f"대상 후보 : {len(coins)}개")

    print("\n공식 5분봉 다운로드 + 10% 눌림 조건 검사...\n")

    candle_success = 0
    candidate_count = 0

    for coin in coins:
        symbol = coin["symbol"]

        if not load_initial_candles(symbol):
            continue

        candle_success += 1

        price = coin["last_price"]

        result = analyze(symbol, price)

        if result is None:
            continue

        watch_symbols.append(symbol)
        candidate_count += 1

        print(
            f"{candidate_count:2d}. "
            f"{symbol:<20}"
            f"거래대금: {coin['volume']:,.0f} "
            f"하락률: {result['drop']:.2f}% "
            f"MA거리: {result['distance']:.3f}%"
        )

    print("\n====== 감시 대상 선정 완료 ======\n")
    print(f"캔들 다운로드 성공 : {candle_success}/{len(coins)}")
    print(f"10% 눌림 조건 만족 : {len(watch_symbols)}개")


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
                else:
                    print(f"❌ 5분봉 갱신 실패 : {symbol}")

            print(f"5분봉 갱신 완료 {success}/{len(watch_symbols)}\n")

            return key

    return last_update


def update_watchlist_if_needed(last_refresh):
    now = datetime.now()

    if (
        now.minute in (0, 30)
        and now.second < 10
    ):
        key = now.strftime("%Y-%m-%d %H:%M")

        if key != last_refresh:
            print("\n====== 감시 대상 자동 갱신 ======\n")

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
    last_watchlist_refresh = None

    while True:
        last_candle_update = update_candles_if_needed(last_candle_update)
        last_watchlist_refresh = update_watchlist_if_needed(
            last_watchlist_refresh
        )

        for symbol in watch_symbols:
            price = get_price(symbol)

            if price is None:
                continue

            result = analyze(symbol, price)

            if result is None:
                continue

            if not result["near_ma"]:
                continue

            # 알림 직전에 공식 5분봉 72개를 다시 받아서 재검증
            if not load_initial_candles(symbol):
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