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
# 主板过滤
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
# 连板高度
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
# 个股评分（强者排序核心🔥）
# =========================
def score_stock(df):

    if len(df) < 60:
        return 0

    df = df.tail(80)

    df["ma5"] = df["收盘"].rolling(5).mean()
    df["ma10"] = df["收盘"].rolling(10).mean()
    df["ma20"] = df["收盘"].rolling(20).mean()

    latest = df.iloc[-1]

    score = 0

    # ===== 趋势 =====
    if latest["ma5"] > latest["ma10"] > latest["ma20"]:
        score += 35

    # ===== 动量 =====
    if df["收盘"].pct_change().iloc[-1] > 0.02:
        score += 15

    # ===== 放量 =====
    vol_ma = df["成交量"].rolling(5).mean().iloc[-1]
    if latest["成交量"] > vol_ma:
        score += 10

    # ===== 突破 =====
    if latest["收盘"] >= df["收盘"].rolling(20).max().iloc[-1]:
        score += 20

    # ===== 加速 =====
    if df["收盘"].pct_change().iloc[-1] > 0.05:
        score += 10

    return score

# =========================
# 仓位控制
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
# 龙头分级（核心🔥）
# =========================
def rank_levels(results):

    if len(results) == 0:
        return [], [], []

    scores = [x[1] for x in results]

    top_s = np.percentile(scores, 95)
    top_a = np.percentile(scores, 85)
    top_b = np.percentile(scores, 70)

    S = []
    A = []
    B = []

    for s, sc in results:
        if sc >= top_s:
            S.append((s, sc))
        elif sc >= top_a:
            A.append((s, sc))
        elif sc >= top_b:
            B.append((s, sc))

    return S, A, B

# =========================
# 主逻辑
# =========================
def main():

    msg = "📊 分层选股 + 龙头分级系统\n\n"

    df = get_market()
    pool = df[df["代码"].apply(is_main)]

    limit_up, limit_down = calc_limit(df)
    max_lb = get_max_board(pool)

    phase = market_phase(limit_up, limit_down, max_lb)
    pos = position(phase)

    msg += f"""
📊 情绪周期：{phase}
涨停：{limit_up}
跌停：{limit_down}
最高连板：{max_lb}

💰 建议仓位：{int(pos*100)}%
"""

    # =========================
    # 强者排序（关键🔥）
    # =========================
    results = []

    for s in pool["代码"].tolist():
        try:
            df_s = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")

            score = score_stock(df_s)

            results.append((s, score))

        except:
            continue

    # 排序
    results = sorted(results, key=lambda x: x[1], reverse=True)

    # =========================
    # 龙头分级（S/A/B）
    # =========================
    S, A, B = rank_levels(results)

    # =========================
    # 输出
    # =========================
    msg += "\n🔥【S级龙头（最强）】\n"
    for s, sc in S[:3]:
        msg += f"{s} | {sc}分\n"

    msg += "\n📊【A级强势股】\n"
    for s, sc in A[:5]:
        msg += f"{s} | {sc}分\n"

    msg += "\n📈【B级观察股】\n"
    for s, sc in B[:5]:
        msg += f"{s} | {sc}分\n"

    msg += "\n📉 风控：只做强者，弱势不参与\n"

    send_telegram(msg)
    print(msg)

# =========================
# 执行
# =========================
if __name__ == "__main__":
    main()
