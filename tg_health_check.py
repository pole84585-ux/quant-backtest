import requests
import os
import time

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def run():
    print("🔥 TG 10秒自检开始\n")

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 环境变量未设置")
        return

    # ===== 第一步 =====
    print("👉 检查 Token...")
    try:
        r = requests.get(f"{BASE_URL}/getMe", timeout=5)
        print("返回：", r.text)
    except Exception as e:
        print("❌ Token请求失败:", e)
        return

    # ===== 第二步 =====
    print("\n👉 测试发送消息...")
    try:
        r = requests.post(
            f"{BASE_URL}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": "🚀 TG测试"
            },
            timeout=5
        )
        print("返回：", r.text)
    except Exception as e:
        print("❌ 发送失败:", e)
        return

    print("\n🎯 TG检测完成")


if __name__ == "__main__":
    run()
