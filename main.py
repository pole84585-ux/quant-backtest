import akshare as ak
import pandas as pd
import numpy as np
import requests
import os
from backtest import backtest_signals

stocks = ["600519", "600036", "601318", "000001", "000858", "300750"]

def send_telegram(msg):
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})


def analyze(df):
    df = df.copy()
    df = df.dropna()

    df["ma5"] = df["收盘"].rolling(5).mean()
    df["ma20"] = df["收盘"].rolling(20).mean()
    df["ret"] = df["收盘"].pct_change()

    signals = []

    for i in range(20, len(df)):
        score = 0

        if df["ma5"].iloc[i] > df["ma20"].iloc[i]:
            score += 1
        if df["ret"].iloc[i] > 0:
            score += 1

        if score >= 2:
            signals.append(i)

    return signals


msg = "📊 A股回测系统报告\n\n"

all_results = []

for s in stocks:
    try:
        df = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
        df = df.tail(120)

        signals = analyze(df)

        result = backtest_signals(df, signals)

        if len(result) == 0:
            continue

        avg3 = result["return_3d"].mean()
        avg5 = result["return_5d"].mean()
        win_rate = (result["return_3d"] > 0).mean()

        all_results.append({
            "stock": s,
            "win_rate": win_rate,
            "avg3": avg3,
            "avg5": avg5,
            "signals": len(result)
        })

        msg += f"""
{s}
信号数：{len(result)}
3日收益：{avg3:.2%}
5日收益：{avg5:.2%}
胜率：{win_rate:.2%}
------------------
"""

    except:
        continue


send_telegram(msg)

print(msg)
