import requests
import time
from config import PUSH_KEY


def send(msg):

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
            time.sleep(1)

            r = requests.post(
                url,
                data=data,
                timeout=10
            )

            if r.status_code == 200:
                print("推送成功")
                return

        except Exception as e:
            print(f"PushDeer失败{i+1}次:", repr(e))

    print("最终推送失败：")
    print(msg)
