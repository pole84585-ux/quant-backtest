import akshare as ak
import pandas as pd
import requests
import os
import time

import matplotlib
matplotlib.use('Agg')   # ✅ 关键：解决GitHub无图形界面
import matplotlib.pyplot as plt


BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")


# ===== Telegram =====
def send_msg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


def send_img(path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(path, "rb") as f:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": f})
    except:
        pass


# ===== 主板过滤 =====
def is_main_board(code):
    return code.startswith(("600","601","603","605","000","001","002"))


# ===== 判断市场状态 =====
try:
    index_df = ak.stock_zh_index_daily(symbol="sh000001")

    if index_df is None or index_df.empty:
        raise Exception("index empty")

    index_df["MA21"] = index_df["close"].rolling(21).mean()

    idx_today = index_df.iloc[-1]

    market_bull = idx_today["close"] >= idx_today["MA21"]

except:
    market_bull = True   # 出错默认当牛市处理


MA_LEN = 21 if market_bull else 34
mode = "牛市(MA21)" if market_bull else "熊市(MA34)"


# ===== 热点板块 =====
stocks = []

try:
    sector_df = ak.stock_board_industry_name_em()

    if sector_df is not None and not sector_df.empty:
        hot_sectors = sector_df.sort_values("涨跌幅", ascending=False).head(8)["板块名称"].tolist()
    else:
        hot_sectors = []

except:
    hot_sectors = []


# ===== 获取板块股票 =====
for sector in hot_sectors:
    try:
        df = ak.stock_board_industry_cons_em(symbol=sector)

        if df is None or df.empty:
            continue

        # ✅ 转 tuple（解决 set 报错）
        stocks.extend([tuple(x) for x in df[["代码","名称"]].values])

        time.sleep(0.5)

    except:
        continue


# ===== 去重 =====
stocks = list(set(stocks))

stock_df = pd.DataFrame(stocks, columns=["code","name"])


# ===== 过滤 =====
stock_df = stock_df[stock_df["code"].apply(is_main_board)]
stock_df = stock_df[~stock_df["name"].str.contains("ST", na=False)]


results = []


# ===== 核心选股 =====
for _, row in stock_df.iterrows():
    code = row["code"]
    name = row["name"]

    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

        if df is None or df.empty or df.shape[0] < 80:
            continue

        df["MA"] = df["收盘"].rolling(MA_LEN).mean()

        if df["MA"].isna().all():
            continue

        today = df.iloc[-1]
        y1 = df.iloc[-2]

        cond_trend = (
            today["收盘"] > today["MA"] and
            y1["收盘"] > y1["MA"]
        )

        cond_pullback = (
            y1["收盘"] <= y1["MA"] and
            today["收盘"] > today["MA"]
        )

        cond_volume = today["成交量"] > y1["成交量"]

        if (cond_trend or cond_pullback) and cond_volume:

            strength = (today["收盘"] - today["MA"]) / today["MA"]
            vol_ratio = today["成交量"] / y1["成交量"]
            momentum = (today["收盘"] - df.iloc[-5]["收盘"]) / df.iloc[-5]["收盘"]

            score = strength*50 + vol_ratio*30 + momentum*20

            results.append((code, name, df, score))

        time.sleep(0.2)

    except:
        continue


# ===== 排序 =====
results.sort(key=lambda x: x[3], reverse=True)


# ===== 画图 =====
def plot(df, code, name):
    df = df.tail(60)

    plt.figure(figsize=(10,5))
    plt.plot(df["收盘"], label="Close")
    plt.plot(df["MA"], label=f"MA{MA_LEN}")
    plt.title(f"{name} {code}")
    plt.legend()

    path = f"/tmp/{code}.png"
    plt.savefig(path)
    plt.close()

    return path


# ===== 输出 =====
if not results:
    send_msg(f"😴 今日无信号 | {mode}")
else:
    send_msg(f"🔥 Top {min(10,len(results))} 机会股 | {mode}")

    for i, (code, name, df, score) in enumerate(results[:10], 1):
        img = plot(df, code, name)
        caption = f"#{i} {name} ({code})\nScore:{round(score,2)}\n{mode}"
        send_img(img, caption)
