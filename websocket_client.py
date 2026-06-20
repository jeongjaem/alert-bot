import json
import threading
import websocket

from state import watch_symbols
from config import BASE_WS
from price_manager import update_price


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

        # 문자열이 오면 무시
        if isinstance(data, str):
            return

        # dict가 아니면 무시
        if not isinstance(data, dict):
            return

        d = data.get("data")

        # data가 dict가 아니면 무시
        if not isinstance(d, dict):
            return

        symbol = d.get("symbol")
        price = d.get("lastPrice")

        if symbol and price:
            update_price(symbol, price)

    except Exception as e:
        print("WebSocket:", e)


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