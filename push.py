import requests
import os
import time

def push(msg):

    key = os.getenv("PUSHDEER_KEY")

    url = f"https://api2.pushdeer.com/message/push"

    params = {
        "pushkey": key,
        "text": msg
    }

    for i in range(3):  # 重试3次
        try:
            r = requests.get(url, params=params, timeout=10)
            print(r.text)
            return
        except Exception as e:
            print(f"retry {i}: {e}")
            time.sleep(3)

    print("Push failed")
