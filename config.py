import os

# 从 GitHub Actions / 系统环境变量读取
PUSHDEER_KEY = os.environ.get("PUSHDEER_KEY")

# 防止空值导致程序崩溃
if not PUSHDEER_KEY:
    raise ValueError("❌ PUSHDEER_KEY 未设置，请在 GitHub Secrets 中配置")
