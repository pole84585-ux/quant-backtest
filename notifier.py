import requests
import time
import os

PUSH_KEY = os.getenv("PUSH_KEY")


def safe_send(msg):

    if not PUSH_KEY:
        print("未配置 PUSH_KEY")
        print(msg)
        return

    url = "https://api2.pushdeer.com/message/push"

    data = {
        "pushkey": PUSH_KEY,
        "text": msg
    }

    for i in range(3):
        try:
            r = requests.post(url, data=data, timeout=10)
            print("Push返回:", r.text)
            return
        except Exception as e:
            print("Push失败:", e)
            time.sleep(2)

    print("最终推送失败")
