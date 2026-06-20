import requests
import time
from datetime import datetime

BASE_URL = "https://contract.mexc.com"

TOP_N = 30
CHECK_INTERVAL = 15
ALERT_COOLDOWN = 30 * 60

DROP_RATE = 10
MA_NEAR_RATE = 0.5

REFRESH_HOURS = [0, 6, 12, 18]

watch_symbols = []
last_refresh_key = None
last_alert_time = {}


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_top30_futures():
    url = f"{BASE_URL}/api/v1/contract/ticker"
    data = requests.get(url, timeout=15).json()

    tickers = data.get("data", [])
    result = []

    for t in tickers:
        symbol = t.get("symbol", "")

        if not symbol.endswith("_USDT"):
            continue

        try:
            gain = float(t.get("riseFallRate", 0)) * 100
            last_price = float(t.get("lastPrice", 0))
        except:
            continue

        result.append({
            "symbol": symbol,
            "gain": gain,
            "last_price": last_price
        })

    result.sort(key=lambda x: x["gain"], reverse=True)
    return result[:TOP_N]


def refresh_watch_symbols():
    global watch_symbols

    top30 = get_top30_futures()
    watch_symbols = [coin["symbol"] for coin in top30]

    print("\n====== MEXC 선물 상승률 TOP30 갱신 ======\n")

    for i, coin in enumerate(top30, 1):
        print(
            f"{i:2d}. {coin['symbol']:<20} "
            f"{coin['gain']:.2f}% "
            f"현재가: {coin['last_price']}"
        )

    print("\n감시 시작\n")


def should_refresh_top30():
    global last_refresh_key

    now = datetime.now()
    refresh_key = now.strftime("%Y-%m-%d %H")

    if now.hour in REFRESH_HOURS and last_refresh_key != refresh_key:
        last_refresh_key = refresh_key
        return True

    return False


def get_5m_candles(symbol):
    end = int(time.time())
    start = end - (6 * 60 * 60)

    url = f"{BASE_URL}/api/v1/contract/kline/{symbol}"

    params = {
        "interval": "Min5",
        "start": start,
        "end": end
    }

    data = requests.get(url, params=params, timeout=15).json()

    if not data.get("success"):
        return []

    d = data.get("data", {})

    times = d.get("time", [])
    opens = d.get("open", [])
    highs = d.get("high", [])
    lows = d.get("low", [])
    closes = d.get("close", [])

    candles = []

    for i in range(len(times)):
        candles.append({
            "time": int(times[i]),
            "open": float(opens[i]),
            "high": float(highs[i]),
            "low": float(lows[i]),
            "close": float(closes[i])
        })

    return candles


def check_signal(symbol):
    candles = get_5m_candles(symbol)

    if len(candles) < 60:
        return None

    recent = candles[-72:]

    high_candle = max(recent, key=lambda x: x["high"])
    low_candle = min(recent, key=lambda x: x["low"])

    high_price = high_candle["high"]
    low_price = low_candle["low"]

    if low_price <= 0:
        return None

    drop = (high_price - low_price) / high_price * 100
    low_after_high = low_candle["time"] > high_candle["time"]

    if drop < DROP_RATE:
        return None

    if not low_after_high:
        return None

    closes = [c["close"] for c in candles]

    ma60 = sum(closes[-60:]) / 60
    current_price = closes[-1]

    distance = abs(current_price - ma60) / ma60 * 100

    if distance <= MA_NEAR_RATE:
        return {
            "symbol": symbol,
            "current_price": current_price,
            "ma60": ma60,
            "distance": distance,
            "drop": drop,
            "high_price": high_price,
            "low_price": low_price,
            "high_time": high_candle["time"],
            "low_time": low_candle["time"]
        }

    return None


def can_alert(symbol):
    last = last_alert_time.get(symbol, 0)
    return time.time() - last >= ALERT_COOLDOWN


def save_alert_time(symbol):
    last_alert_time[symbol] = time.time()


def main():
    print("MEXC 선물 재반등 감시봇 시작")
    refresh_watch_symbols()

    while True:
        try:
            if should_refresh_top30():
                refresh_watch_symbols()

            for symbol in watch_symbols:
                try:
                    signal = check_signal(symbol)

                    if signal and can_alert(symbol):
                        save_alert_time(symbol)

                        print("\n🚨 MA60 접근 알림")
                        print(f"시간: {now_text()}")
                        print(f"코인: {signal['symbol']}")
                        print(f"현재가: {signal['current_price']}")
                        print(f"5분봉 60선: {signal['ma60']}")
                        print(f"MA60 거리: {signal['distance']:.3f}%")
                        print(f"최근 고점: {signal['high_price']}")
                        print(f"최근 저점: {signal['low_price']}")
                        print(f"고점 대비 하락률: {signal['drop']:.2f}%")
                        print("30분 동안 같은 코인 재알림 안 함\n")

                    time.sleep(0.15)

                except Exception as e:
                    print(f"{symbol} 확인 중 오류: {e}")

            print(f"{now_text()} 감시 중... 대상 {len(watch_symbols)}개")
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("봇 종료")
            break

        except Exception as e:
            print("전체 오류:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()