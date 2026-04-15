import akshare as ak
import pandas as pd
import requests
import os
import time
import matplotlib.pyplot as plt

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

# ===== Telegram =====
def send_msg(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def send_img(path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": f})

# ===== 主板过滤 =====
def is_main_board(code):
    return code.startswith(("600","601","603","605","000","001","002"))

# ===== 计算上证指数均线 =====
index_df = ak.stock_zh_index_daily(symbol="sh000001")
index_df["MA21"] = index_df["close"].rolling(21).mean()

today_index = index_df.iloc[-1]
market_bull = today_index["close"] >= today_index["MA21"]

MA_LEN = 21 if market_bull else 34
mode = "牛市(MA21)" if market_bull else "熊市(MA34)"

# ===== 热点板块 =====
sector_df = ak.stock_board_industry_name_em()
hot_sectors = sector_df.sort_values("涨跌幅", ascending=False).head(10)["板块名称"].tolist()

stocks = []

for s in hot_sectors:
    try:
        df = ak.stock_board_industry_cons_em(symbol=s)
        stocks.extend([tuple(x) for x in df[["代码","名称"]].values])
 stocks = list(set(stocks))
        time.sleep(0.5)
    except:
        continue

stocks = list(set(stocks))
stock_df = pd.DataFrame(stocks, columns=["code","name"])

# ===== 过滤 =====
stock_df = stock_df[stock_df["code"].apply(is_main_board)]
stock_df = stock_df[~stock_df["name"].str.contains("ST")]

results = []

# ===== 选股 =====
for _, row in stock_df.iterrows():
    code = row["code"]
    name = row["name"]

    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

        if df.shape[0] < 80:
            continue

        df["MA"] = df["收盘"].rolling(MA_LEN).mean()

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
    send_msg(f"😴 今日无信号 | 模式: {mode}")
else:
    send_msg(f"🔥 信号股票 Top {min(10,len(results))} | {mode}")

    for i, (code, name, df, score) in enumerate(results[:10], 1):
        img = plot(df, code, name)
        caption = f"#{i} {name} ({code})\nScore:{round(score,2)}\n{mode}"
        send_img(img, caption)
