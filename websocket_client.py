import json
import threading
import time
import websocket

from config import BASE_WS
from price_manager import update_price
from state import watch_symbols


ws = None
running = False


def subscribe_symbols():
    global ws

    if ws is None:
        return

    count = 0

    for symbol in watch_symbols:
        msg = {
            "method": "sub.ticker",
            "param": {
                "symbol": symbol
            }
        }

        try:
            ws.send(json.dumps(msg))
            count += 1
        except Exception as e:
            print("구독 실패:", symbol, e)

    print(f"{count}개 코인 구독 완료")


def on_open(socket):
    print("✅ WebSocket 연결 성공")
    subscribe_symbols()


def on_message(socket, message):
    try:
        data = json.loads(message)

        if isinstance(data, str):
            return

        if not isinstance(data, dict):
            return

        d = data.get("data")

        if not isinstance(d, dict):
            return

        symbol = d.get("symbol")
        price = d.get("lastPrice")

        if symbol and price:
            update_price(symbol, price)

    except Exception as e:
        print("WebSocket 메시지 오류:", e)


def on_error(socket, error):
    print("WebSocket 오류 :", error)


def on_close(socket, code, msg):
    print("WebSocket 종료")


def ping_loop():
    global ws

    while True:
        try:
            if ws:
                ws.send(json.dumps({"method": "ping"}))
        except Exception:
            pass

        time.sleep(15)


def websocket_loop():
    global ws, running

    while running:
        ws = websocket.WebSocketApp(
            BASE_WS,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        ws.run_forever()

        if running:
            print("WebSocket 5초 후 재연결")
            time.sleep(5)


def start():
    global running

    if running:
        return

    running = True

    threading.Thread(
        target=websocket_loop,
        daemon=True
    ).start()

    threading.Thread(
        target=ping_loop,
        daemon=True
    ).start()


def resubscribe():
    global ws

    print("\nWebSocket 재구독 중...")

    if ws:
        try:
            ws.close()
        except Exception:
            pass

    print("WebSocket 재연결 대기\n")