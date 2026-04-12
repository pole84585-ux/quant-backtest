import akshare as ak
import pandas as pd
import numpy as np
import requests
import os

# =========================
# Telegram
# =========================
def send_telegram(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# =========================
# 股票过滤（主板）
# =========================
def is_main(code):
    return code.startswith(("600","601","603","605","000","001","002"))

# =========================
# 市场数据
# =========================
def get_market():
    return ak.stock_zh_a_spot_em()

# =========================
# 情绪周期
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
# 涨跌停统计
# =========================
def calc_limit(df):
    return len(df[df["涨跌幅"] >= 9.5]), len(df[df["涨跌幅"] <= -9.5])

# =========================
# 连板高度（简化）
# =========================
def get_max_board(pool):
    max_lb = 0

    for s in pool[:80]:
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
# 龙头池
# =========================
def get_leaders(df):
    df = df.sort_values(by="涨跌幅", ascending=False)
    return df[df["涨跌幅"] > 5]["代码"].tolist()[:30]

# =========================
# 个股评分（核心）
# =========================
def score_stock(df):

    df = df.tail(80)

    df["ma5"] = df["收盘"].rolling(5).mean()
    df["ma10"] = df["收盘"].rolling(10).mean()
    df["ma20"] = df["收盘"].rolling(20).mean()

    latest = df.iloc[-1]

    score = 0

    # ===== 趋势 =====
    if latest["ma5"] > latest["ma10"] > latest["ma20"]:
        score += 40

    # ===== 动量 =====
    if df["收盘"].pct_change().iloc[-1] > 0.03:
        score += 20

    # ===== 放量 =====
    vol_ma = df["成交量"].rolling(5).mean().iloc[-1]
    if latest["成交量"] > vol_ma:
        score += 10

    # ===== 突破 =====
    if latest["收盘"] >= df["收盘"].rolling(20).max().iloc[-1]:
        score += 20

    return score

# =========================
# 卖出信号
# =========================
def sell_signal(df, phase):

    df = df.tail(50)
    df["ma10"] = df["收盘"].rolling(10).mean()

    latest = df.iloc[-1]

    # 跌破均线
    if latest["收盘"] < latest["ma10"]:
        return True

    # 退潮
    if phase == "❄️退潮":
        return True

    # 放量下跌
    if df["收盘"].pct_change().iloc[-1] < -0.03:
        return True

    return False

# =========================
# 仓位
# =========================
def position(phase):

    if phase == "🚀主升":
        return 0.25

    if phase == "🟡启动":
        return 0.15

    if phase == "🔥高潮":
        return 0.10

    return 0.0

# =========================
# 主逻辑
# =========================
def main():

    msg = "📊 龙头完整交易系统\n\n"

    df = get_market()
    pool = df[df["代码"].apply(is_main)]

    limit_up, limit_down = calc_limit(df)
    max_lb = get_max_board(pool)

    phase = market_phase(limit_up, limit_down, max_lb)
    pos = position(phase)

    msg += f"""
📊 情绪周期：
涨停：{limit_up}
跌停：{limit_down}
最高连板：{max_lb}

👉 当前阶段：{phase}
💰 建议仓位：{int(pos*100)}%
"""

    leaders = get_leaders(df)

    candidates = []
    holdings = []

    # =========================
    # 排序模型（核心）
    # =========================
    for s in leaders:
        try:
            df_s = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
            score = score_stock(df_s)

            if score >= 70:
                candidates.append((s, score))

        except:
            continue

    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)

    # =========================
    # 买入
    # =========================
    msg += "\n🔥【买入候选】\n"
    for s, sc in candidates[:5]:
        msg += f"{s} | {sc}分 | 仓位{int(pos*100)}%\n"

    # =========================
    # 卖出逻辑（模拟持仓检查）
    # =========================
    msg += "\n📉【卖出信号】\n"

    for s, sc in candidates[:5]:
        try:
            df_s = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")

            if sell_signal(df_s, phase):
                msg += f"{s} ❌ 卖出信号\n"
        except:
            continue

    # =========================
    # 换龙头逻辑
    # =========================
    msg += "\n🔁【换龙头信号】\n"

    if len(candidates) >= 2:
        if candidates[0][1] - candidates[1][1] > 15:
            msg += f"👉 龙头切换：{candidates[0][0]} 强于其他\n"
        else:
            msg += "暂无明显新龙头\n"

    msg += "\n📉 风控：趋势为王，退潮空仓\n"

    send_telegram(msg)
    print(msg)

# =========================
# 执行
# =========================
if __name__ == "__main__":
    main()
