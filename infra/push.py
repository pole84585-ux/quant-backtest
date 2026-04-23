import os
from infra.net import safe_get

def push(msg):

    key = os.getenv("PUSHDEER_KEY")

    if not key:
        print("[PUSH] no key, fallback log:")
        print(msg)
        return

    url = "https://api2.pushdeer.com/message/push"

    params = {
        "pushkey": key,
        "text": msg
    }

    res = safe_get(url, params=params)

    if res is None:
        print("[PUSH FAILED - fallback]")
        print(msg)
    else:
        print("[PUSH OK]")
