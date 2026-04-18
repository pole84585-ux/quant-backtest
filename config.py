import os

# ===== PushDeer =====
PUSH_KEY = os.getenv("PUSH_KEY") or ""

# ===== Telegram =====
TG_TOKEN = os.getenv("TG_TOKEN") or ""
TG_CHAT_ID = os.getenv("TG_CHAT_ID") or ""

# ===== 开关 =====
ENABLE_PUSHDEER = True
ENABLE_TELEGRAM = True
