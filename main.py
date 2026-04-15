import requests
import os

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# =====================
# 1️⃣ 检查 token 是否有效
# =====================
def check_token():
    url = f"{BASE}/getMe"
    r = requests.get(url)
    print("\n[1] Token检查结果：")
    print(r.text)

    try:
        data = r.json()
        return data.get("ok", False)
    except:
        return False

# =====================
# 2️⃣ 检查 chat_id
# =====================
def check_chat():
    url = f"{BASE}/getUpdates"
    r = requests.get(url)

    print("\n[2] Chat检查结果（最近消息）：")
    print(r.text)

    return r.status_code == 200

# =====================
# 3️⃣ 测试发送消息
# =====================
def test_send():
    url = f"{BASE}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": "🚀 TG诊断测试：如果你收到说明全部正常"
    })

    print("\n[3] 发送测试结果：")
    print(r.text)

    try:
        return r.json().get("ok", False)
    except:
        return False

# =====================
# 主程序
# =====================
def run():
    print("🔥 TG 诊断开始\n")

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN 为空")
        return

    if not CHAT_ID:
        print("❌ CHAT_ID 为空")
        return

    token_ok = check_token()
    chat_ok = check_chat()
    send_ok = test_send()

    print("\n======================")
    print("📊 诊断总结：")

    if token_ok:
        print("✅ Token 正常")
    else:
        print("❌ Token 异常")

    if chat_ok:
        print("✅ Chat API 正常")
    else:
        print("❌ Chat API 异常")

    if send_ok:
        print("✅ 消息发送成功")
    else:
        print("❌ 消息发送失败")

    print("======================\n")

if __name__ == "__main__":
    run()
