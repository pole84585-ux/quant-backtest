import requests
from config import BOT_TOKEN, CHAT_ID


def send(msg):

    if not BOT_TOKEN or not CHAT_ID:
        print("未配置TG，输出如下：")
        print(msg)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("TG发送失败:", e)
