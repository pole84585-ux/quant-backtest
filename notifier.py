import requests
import time
from config import (
    PUSH_KEY,
    TG_TOKEN,
    TG_CHAT_ID,
    ENABLE_PUSHDEER,
    ENABLE_TELEGRAM
)


# ===== PushDeer =====
def send_pushdeer(msg):

    if not PUSH_KEY:
        return False

    try:
        r = requests.post(
            "https://api2.pushdeer.com/message/push",
            data={
                "pushkey": PUSH_KEY,
                "text": msg
            },
            timeout=10
        )
        return r.status_code == 200
    except:
        return False


# ===== Telegram =====
def send_telegram(msg):

    if not TG_TOKEN or not TG_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            data={
                "chat_id": TG_CHAT_ID,
                "text": msg
            },
            timeout=10
        )
        return r.status_code == 200
    except:
        return False


# ===== 主入口（自动切换）=====
def send(msg):

    success = False

    # 主通道 PushDeer
    if ENABLE_PUSHDEER:
        success = send_pushdeer(msg)

    # 备通道 Telegram
    if not success and ENABLE_TELEGRAM:
        success = send_telegram(msg)

    if success:
        print("推送成功")
    else:
        print("推送失败")
        print(msg)
