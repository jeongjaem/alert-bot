import json
import threading
import websocket

from config import BASE_WS
from state import latest_price, watch_symbols


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

        if "data" not in data:
            return

        d = data["data"]

        symbol = d.get("symbol")
        price = d.get("lastPrice")

        if symbol and price:
            latest_price[symbol] = float(price)

    except Exception as e:
        print(e)


def on_error(ws, error):
    print("WebSocket 오류 :", error)


def on_close(ws, code, msg):
    print("WebSocket 종료")


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