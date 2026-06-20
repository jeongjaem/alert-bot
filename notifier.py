import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            },
            timeout=10,
        )

        if r.status_code != 200:
            print("Telegram 전송 실패:", r.text)

    except Exception as e:
        print("Telegram 오류:", e)


def send_test_alert():
    send_alert("✅ MEXC 알림봇 테스트 성공")