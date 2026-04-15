import requests
import os
import time

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# 1️⃣ 检查 Token
# =========================
def check_token():
    try:
        r = requests.get(f"{BASE_URL}/getMe", timeout=5)
        data = r.json()

        if data.get("ok"):
            print("✅ Token 正常")
            return True
        else:
            print("❌ Token 无效")
            print(data)
            return False
    except Exception as e:
        print("❌ Token检查失败:", str(e))
        return False


# =========================
# 2️⃣ 测试发送消息
# =========================
def test_send():
    try:
        r = requests.post(
            f"{BASE_URL}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": "🚀 TG 10秒自检：测试消息"
            },
            timeout=5
        )

        data = r.json()

        if data.get("ok"):
            print("✅ 消息发送成功")
            return True, None
        else:
            print("❌ 发送失败")
            return False, data

    except Exception as e:
        print("❌ 网络/请求失败:", str(e))
        return False, str(e)


# =========================
# 3️⃣ 错误诊断
# =========================
def diagnose(send_result):
    success, err = send_result

    if success:
        print("\n🎯 TG状态：完全正常")
        return

    print("\n🚨 TG异常诊断：")

    if isinstance(err, dict):
        code = err.get("error_code")

        if code == 400:
            print("👉 chat_id错误 或 bot未启动")
        elif code == 401:
            print("👉 token错误")
        elif code == 403:
            print("👉 bot被拉黑 / 未点击start")
        else:
            print("👉 未知API错误:", err)

    else:
        print("👉 网络问题 / 请求失败")


# =========================
# 4️⃣ 主流程（10秒内完成）
# =========================
def run():
    start = time.time()

    print("🔥 TG 10秒自检开始\n")

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 环境变量未设置")
        return

    token_ok = check_token()
    send_result = test_send()
    diagnose(send_result)

    cost = time.time() - start
    print(f"\n⏱️ 总耗时: {cost:.2f} 秒")


if __name__ == "__main__":
    run()
