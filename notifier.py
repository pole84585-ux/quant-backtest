import requests
from config import BOT_TOKEN, CHAT_ID
from cache import load_cache, save_cache


cache = load_cache()


def send(msg):

    if not BOT_TOKEN or not CHAT_ID:
        print(msg)
        return

    key = str(hash(msg))

    if key in cache:
        print("重复信号跳过")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    success = False

    for i in range(3):
        try:
            r = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "text": msg
                },
                timeout=10
            )

            if r.status_code == 200:
                success = True
                break

        except Exception as e:
            print(f"TG失败{i+1}:", e)

    if success:
        cache.add(key)
        save_cache(cache)
        print("发送成功")
    else:
        print("发送失败:", msg)
