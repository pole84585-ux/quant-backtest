import akshare as ak
import pandas as pd
import numpy as np
import requests
import os
import time
import random
import json

# =========================
# Telegram
# =========================
def send(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=10)
    except:
        print("TG失败")

# =========================
# 持仓文件（本地模拟账户）
# =========================
POSITION_FILE = "position.json"

def load_position():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "r") as f:
            return json.load(f)
    return {}

def save_position(pos):
    with open(POSITION_FILE, "w") as f:
        json.dump(pos, f)

# =========================
# 安全获取数据
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
# 评分
# =========================
def score(df):
    df = df.tail(60)
    ma5 = df["收盘"].rolling(5).mean().iloc[-1]
    ma10 = df["收盘"].rolling(10).mean().iloc[-1]
    ma20 = df["收盘"].rolling(20).mean().iloc[-1]
    pct = df["收盘"].pct_change().iloc[-1]

    sc = 0
    if ma5 > ma10: sc += 20
    if ma10 > ma20: sc += 20
    if pct > 0: sc += 20
    if pct > 0.03: sc += 20
    return sc

# =========================
# 主逻辑
# =========================
def main():

    msg = "📊 交易执行系统\n\n"

    market = ak.stock_zh_a_spot_em()
    pool = market["代码"].tolist()

    pool = random.sample(pool, 100)

    results = []

    for s in pool:
        df = safe_fetch(s)
        if df is None:
            continue

        sc = score(df)
        results.append((s, sc, df))

        time.sleep(0.1)

    results = sorted(results, key=lambda x: x[1], reverse=True)

    top = results[:3]

    # =========================
    # 持仓读取
    # =========================
    pos = load_position()

    msg += "🔥【今日龙头】\n"
    for s, sc, _ in top:
        msg += f"{s} | {sc}\n"

    # =========================
    # 买入逻辑
    # =========================
    for s, sc, df in top:

        price = df["收盘"].iloc[-1]

        if s not in pos:
            pos[s] = {"buy_price": price}
            msg += f"\n🟢 买入：{s} @ {price}"

    # =========================
    # 卖出逻辑
    # =========================
    for s in list(pos.keys()):

        df = safe_fetch(s)
        if df is None:
            continue

        price = df["收盘"].iloc[-1]
        buy = pos[s]["buy_price"]

        ret = (price - buy) / buy

        ma5 = df["收盘"].rolling(5).mean().iloc[-1]

        # 止损
        if ret < -0.05:
            msg += f"\n🔴 止损卖出：{s} {ret:.2%}"
            del pos[s]
            continue

        # 止盈
        if ret > 0.10:
            msg += f"\n💰 止盈卖出：{s} {ret:.2%}"
            del pos[s]
            continue

        # 跌破均线
        if price < ma5:
            msg += f"\n⚠️ 走弱卖出：{s}"
            del pos[s]
            continue

        # 不在龙头 → 换股
        if s not in [x[0] for x in top]:
            msg += f"\n🔁 换股卖出：{s}"
            del pos[s]

    save_position(pos)

    msg += "\n\n📦 当前持仓：\n"
    for s in pos:
        msg += f"{s}\n"

    send(msg)
    print(msg)

if __name__ == "__main__":
    main()
