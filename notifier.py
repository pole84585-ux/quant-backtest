import requests
import time
from config import BOT_TOKEN, CHAT_ID


session = requests.Session()


def send(msg):

    if not BOT_TOKEN or not CHAT_ID:
        print(msg)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Connection": "keep-alive"
    }

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    for i in range(3):

        try:
            time.sleep(1)  # ⭐关键：防止瞬发触发风控

            r = session.post(
                url,
                data=payload,
                headers=headers,
                timeout=15
            )

            if r.status_code == 200:
                return

            print("TG返回异常:", r.text)

        except requests.exceptions.RequestException as e:
            print(f"TG失败第{i+1}次:", repr(e))

    print("最终发送失败：")
    print(msg)
