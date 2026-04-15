import requests
from config import TG_TOKEN, TG_CHAT_ID

def send_msg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

    try:
        r = requests.post(url, data={
            "chat_id": TG_CHAT_ID,
            "text": text[:3500]  # 防止超长
        }, timeout=10)

        print(r.text)

    except Exception as e:
        print("TG错误:", e)
