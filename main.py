from strategy import select
from tg import send_msg
from datetime import datetime

def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    mode, data = select()

    if not data:
        send_msg(f"📭 {now}\n模式:{mode}\n无机会")
        return

    msg = f"📊 {now} 牛熊 v2.0系统\n市场:{mode}\n\n"

    for c, m, state, s in data[:10]:
        msg += f"{c} | {state} | 评分:{s}\n"

    send_msg(msg)

if __name__ == "__main__":
    run()
