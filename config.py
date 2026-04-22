import os

PUSHDEER_KEY = os.getenv("PUSHDEER_KEY")

if not PUSHDEER_KEY:
    raise ValueError("❌ PUSHDEER_KEY 未设置，请在 GitHub Secrets 中配置")
