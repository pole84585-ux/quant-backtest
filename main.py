import akshare as ak
import pandas as pd
import numpy as np
import requests
import os
import time

# =========================
# TG
# =========================
def send(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# =========================
# 主板过滤
# =========================
def is_main(code):
    return code.startswith(("600","601","603","605","000","001","002","003","004"))

# =========================
# 大盘过滤🔥
# =========================
def market_ok():
    df = ak.stock_zh_index_daily(symbol="sh000001")
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    return df.iloc[-1]["ma5"] > df.iloc[-1]["ma20"]

# =========================
# 热点板块🔥
# =========================
def get_hot_sectors():
    try:
        df = ak.stock_board_industry_name_em()
        df = df.sort_values(by="涨跌幅", ascending=False)
        return df.head(5)["板块名称"].tolist()
    except:
        return []

# =========================
# 板块成分
# =========================
def get_sector_stocks(name):
    try:
        df = ak.stock_board_industry_cons_em(symbol=name)
        return df["代码"].tolist()
    except:
        return []

# =========================
# 安全获取
# =========================
def safe_fetch(s):
    try:
        df = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
        if df is not None and len(df) > 30:
            return df
    except:
        return None
    return None

# =========================
# 起爆点🔥
# =========================
def detect_start(df):

    df = df.tail(30)
    df["ma5"] = df["收盘"].rolling(5).mean()
    df["ma10"] = df["收盘"].rolling(10).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    cond1 = prev["ma5"] < prev["ma10"] and latest["ma5"] > latest["ma10"]
    cond2 = latest["收盘"] > prev["收盘"]
    cond3 = latest["成交量"] > df["成交量"].rolling(5).mean().iloc[-1]

    return cond1 and cond2 and cond3

# =========================
# 强度评分🔥
# =========================
def score(df):

    df = df.tail(60)

    ma5 = df["收盘"].rolling(5).mean().iloc[-1]
    ma10 = df["收盘"].rolling(10).mean().iloc[-1]
    ma20 = df["收盘"].rolling(20).mean().iloc[-1]

    price = df["收盘"].iloc[-1]
    pct = df["收盘"].pct_change().iloc[-1]

    s = 0
    if ma5 > ma10 > ma20: s += 40
    if pct > 0: s += 20
    if pct > 0.03: s += 20
    if price > df["收盘"].max()*0.9: s += 20

    return s

# =========================
# 主程序🔥
# =========================
def main():

    msg = "📊 起爆点 + 龙头系统\n\n"

    # ===== 大盘 =====
    if not market_ok():
        msg += "❄️ 市场弱 → 今日不做\n"
        send(msg)
        print(msg)
        return

    msg += "🚀 市场允许交易\n\n"

    # ===== 热点板块 =====
    sectors = get_hot_sectors()

    msg += "🔥 热点板块：\n"
    for s in sectors:
        msg += f"{s}\n"

    final = []

    # ===== 板块循环 =====
    for sec in sectors:

        stocks = get_sector_stocks(sec)

        temp = []

        for s in stocks[:20]:  # 限流

            if not is_main(s):
                continue

            df = safe_fetch(s)
            if df is None:
                continue

            sc = score(df)

            # 👉 龙头候选（先强度）
            temp.append((s, sc, df))

            time.sleep(0.1)

        # ===== 选龙头 =====
        temp = sorted(temp, key=lambda x: x[1], reverse=True)

        leaders = temp[:3]

        # ===== 龙头中找启动 =====
        for s, sc, df in leaders:
            if detect_start(df):
                final.append((sec, s, sc))

    # ===== 输出 =====
    msg += "\n🚀【主升起爆龙头】\n"

    if len(final) == 0:
        msg += "（暂无符合条件）\n"
    else:
        for sec, s, sc in final[:5]:
            msg += f"{sec}：{s} | {sc}\n"

    msg += """
\n📌 买点：14:30 或 次日开盘
📉 止损：-5%
💰 止盈：+10%
"""

    send(msg)
    print(msg)

if __name__ == "__main__":
    main()
