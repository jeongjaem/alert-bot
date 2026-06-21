import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_alert(message):

    if (
        TELEGRAM_BOT_TOKEN == "8947816525:AAHhdSqVlpUPes93_QxdIclY6t9TfRE4ib0"
        or TELEGRAM_CHAT_ID == "5120651068"
    ):
        return

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:
        requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            },
            timeout=10,
        )
    except Exception as e:
        print("Telegram 오류:", e)