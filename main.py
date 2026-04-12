import akshare as ak
import pandas as pd
import numpy as np
import requests
import os

# =========================
# Telegram 推送
# =========================
def send_telegram(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# =========================
# 主板过滤
# =========================
def is_main(code):
    return code.startswith(("600","601","603","605","000","001","002"))

# =========================
# 获取市场数据
# =========================
def get_market():
    return ak.stock_zh_a_spot_em()

# =========================
# 涨停 / 跌停统计
# =========================
def calc_limit(df):
    limit_up = df[df["涨跌幅"] >= 9.5]
    limit_down = df[df["涨跌幅"] <= -9.5]
    return len(limit_up), len(limit_down)

# =========================
# 连板高度（简化版）
# =========================
def get_max_board(pool):
    max_lb = 0

    for s in pool[:100]:
        try:
            df = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
            df = df.tail(10)

            lb = 0
            for i in range(len(df)-1, 0, -1):
                if df["收盘"].iloc[i] / df["收盘"].iloc[i-1] > 1.095:
                    lb += 1
                else:
                    break

            max_lb = max(max_lb, lb)

        except:
            continue

    return max_lb

# =========================
# 情绪周期判断
# =========================
def market_phase(limit_up, limit_down, max_lb):

    if limit_down > 50:
        return "❄️退潮"

    if max_lb >= 5 and limit_up > 80:
        return "🔥高潮"

    if max_lb >= 3 and limit_up > 40:
        return "🚀主升"

    if limit_up > 20:
        return "🟡启动"

    return "⚪冰点"

# =========================
# 龙头识别
# =========================
def get_leaders(df):
    df = df.sort_values(by="涨跌幅", ascending=False)

    leaders = df[df["涨跌幅"] > 5]["代码"].tolist()

    return leaders[:20]

# =========================
# 龙头评分
# =========================
def analyze_stock(df):
    df["ma5"] = df["收盘"].rolling(5).mean()
    df["ma10"] = df["收盘"].rolling(10).mean()
    df["ma20"] = df["收盘"].rolling(20).mean()

    ema12 = df["收盘"].ewm(span=12).mean()
    ema26 = df["收盘"].ewm(span=26).mean()
    dif = ema12 - ema26

    score = 0

    # 均线多头
    if df["ma5"].iloc[-1] > df["ma10"].iloc[-1] > df["ma20"].iloc[-1]:
        score += 30
    else:
        return 0

    # MACD
    if dif.iloc[-1] > 0:
        score += 30

    # 动量
    if df["收盘"].pct_change().iloc[-1] > 0:
        score += 20

    # 新高
    if df["收盘"].iloc[-1] >= df["收盘"].rolling(20).max().iloc[-1]:
        score += 20

    return score

# =========================
# 仓位控制（核心🔥）
# =========================
def position_by_phase(phase):

    if phase == "🚀主升":
        return 0.25

    if phase == "🟡启动":
        return 0.15

    if phase == "🔥高潮":
        return 0.10

    if phase == "❄️退潮":
        return 0.0

    return 0.05

# =========================
# 主逻辑
# =========================
def main():

    msg = "📊 龙头接力 + 情绪周期系统\n\n"

    df = get_market()

    pool = df[df["代码"].apply(is_main)]

    limit_up, limit_down = calc_limit(df)
    max_lb = get_max_board(pool)

    phase = market_phase(limit_up, limit_down, max_lb)
    pos = position_by_phase(phase)

    msg += f"""
📊 情绪周期：
涨停：{limit_up}
跌停：{limit_down}
最高连板：{max_lb}

👉 当前阶段：{phase}
💰 建议仓位：{int(pos*100)}%
"""

    # ===== 龙头筛选 =====
    leaders = get_leaders(df)

    buy_list = []

    for s in leaders:
        try:
            hist = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
            hist = hist.tail(80)

            score = analyze_stock(hist)

            if score >= 70:
                buy_list.append((s, score))

        except:
            continue

    buy_list = sorted(buy_list, key=lambda x: x[1], reverse=True)[:5]

    msg += "\n🔥【龙头接力买入】\n"

    if pos == 0:
        msg += "当前退潮期，建议空仓\n"
    else:
        for s, sc in buy_list:
            msg += f"{s} | {sc}分 | 仓位{int(pos*100)}%\n"

    msg += "\n📉 风控：顺势而为，退潮空仓\n"

    send_telegram(msg)
    print(msg)

# =========================
# 执行
# =========================
if __name__ == "__main__":
    main()
