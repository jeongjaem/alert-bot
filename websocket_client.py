import json
import threading
import time
import websocket

from config import BASE_WS
from price_manager import update_price
from state import watch_symbols


ws = None


def on_open(ws):
    print("✅ WebSocket 연결 성공")

    for symbol in watch_symbols:
        msg = {
            "method": "sub.ticker",
            "param": {
                "symbol": symbol
            }
        }
        ws.send(json.dumps(msg))

    print(f"{len(watch_symbols)}개 코인 구독 완료")


def on_message(ws, message):
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


def on_error(ws, error):
    print("WebSocket 오류 :", error)


def on_close(ws, code, msg):
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


def start():
    global ws

    ws = websocket.WebSocketApp(
        BASE_WS,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    threading.Thread(
        target=ws.run_forever,
        daemon=True
    ).start()

    threading.Thread(
        target=ping_loop,
        daemon=True
    ).start()