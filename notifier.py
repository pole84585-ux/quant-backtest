import requests
from config import BOT_TOKEN, CHAT_ID


def send(msg):

    if not BOT_TOKEN or not CHAT_ID:
        print("TG未配置")
        print(msg)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for i in range(3):  # 重试3次
        try:
            r = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "text": msg
                },
                timeout=10  # ⭐关键
            )

            if r.status_code == 200:
                return

        except Exception as e:
            print(f"TG失败第{i+1}次:", e)

    print("最终发送失败：", msg)
