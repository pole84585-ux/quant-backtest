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
# 市场数据
# =========================
def get_market():
    return ak.stock_zh_a_spot_em()

# =========================
# 情绪判断
# =========================
def calc_limit(df):
    return len(df[df["涨跌幅"] >= 9.5]), len(df[df["涨跌幅"] <= -9.5])

def market_phase(up, down):
    if down > 50:
        return "❄️退潮"
    if up > 80:
        return "🔥高潮"
    if up > 40:
        return "🚀主升"
    if up > 20:
        return "🟡启动"
    return "⚪冰点"

# =========================
# 获取板块（核心🔥）
# =========================
def get_hot_sectors():
    try:
        df = ak.stock_board_industry_name_em()
        df = df.sort_values(by="涨跌幅", ascending=False)
        return df.head(5)["板块名称"].tolist()
    except:
        return []

# =========================
# 板块成分股
# =========================
def get_sector_stocks(name):
    try:
        df = ak.stock_board_industry_cons_em(symbol=name)
        return df["代码"].tolist()
    except:
        return []

# =========================
# 启动检测（优化版🔥）
# =========================
def detect_start(df):

    if len(df) < 40:
        return False

    df = df.tail(40)

    pct = df["收盘"].pct_change().iloc[-1]
    vol_ma = df["成交量"].rolling(5).mean().iloc[-1]

    return (0 < pct < 0.06) and (df["成交量"].iloc[-1] > vol_ma)

# =========================
# 强度评分（优化版🔥）
# =========================
def score_stock(df):

    if len(df) < 40:
        return 0

    df = df.tail(60)

    ma5 = df["收盘"].rolling(5).mean().iloc[-1]
    ma10 = df["收盘"].rolling(10).mean().iloc[-1]
    ma20 = df["收盘"].rolling(20).mean().iloc[-1]

    pct = df["收盘"].pct_change().iloc[-1]

    score = 0

    if ma5 > ma10 > ma20: score += 40
    if pct > 0: score += 20
    if pct > 0.03: score += 20

    return score

# =========================
# 主逻辑
# =========================
def main():

    msg = "📊 主升浪高胜率系统\n\n"

    market = get_market()
    up, down = calc_limit(market)
    phase = market_phase(up, down)

    msg += f"""
📊 情绪：{phase}
涨停：{up} | 跌停：{down}
"""

    # =========================
    # 热点板块
    # =========================
    sectors = get_hot_sectors()

    msg += "\n🔥 热点板块：\n"
    for s in sectors:
        msg += f"{s}\n"

    final_picks = []

    # =========================
    # 板块内选股
    # =========================
    for sec in sectors:

        stocks = get_sector_stocks(sec)

        results = []

        for s in stocks[:30]:   # 限制数量
            try:
                df = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")

                score = score_stock(df)

                # 启动或强势
                if detect_start(df) or score > 60:
                    results.append((s, score))

            except:
                continue

        results = sorted(results, key=lambda x: x[1], reverse=True)

        if len(results) > 0:
            final_picks.append((sec, results[0]))  # 每板块选龙头

    # =========================
    # 输出
    # =========================
    msg += "\n🚀【主升浪龙头】\n"

    for sec, (s, sc) in final_picks:
        msg += f"{sec}：{s} | {sc}\n"

    msg += "\n📉 风控：只做热点板块龙头\n"

    send_telegram(msg)
    print(msg)

if __name__ == "__main__":
    main()
