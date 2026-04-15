import akshare as ak
import pandas as pd
import requests
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import time
from datetime import datetime

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

# ===== TG =====
def send_msg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("TG错误:", e)

def send_img(path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(path, "rb") as f:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": f})
    except Exception as e:
        print("TG图片错误:", e)

# ===== 主板过滤 =====
def is_main(code):
    return code.startswith(("600","601","603","605","000","001","002"))

def is_bad(name):
    return "ST" in name

# ===== 牛熊判断 =====
def get_market():
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df["ma21"] = df["close"].rolling(21).mean()
        last = df.iloc[-1]
        return last["close"] >= last["ma21"]
    except:
        return True

is_bull = get_market()
MA = 21 if is_bull else 34
mode = "牛市(MA21)" if is_bull else "熊市(MA34)"

# ===== 热点板块（带兜底）=====
def get_sectors():
    try:
        df = ak.stock_board_industry_name_em()
        if df is None or df.empty:
            raise Exception

        if "涨跌幅" in df.columns:
            return df.sort_values("涨跌幅", ascending=False).head(6)["板块名称"].tolist()

        return df["板块名称"].head(6).tolist()

    except:
        return ["半导体","人工智能","新能源","证券","消费电子"]

sectors = get_sectors()
print("板块:", sectors)

# ===== 股票池 =====
stocks = []

for s in sectors:
    try:
        df = ak.stock_board_industry_cons_em(symbol=s)
        if df is None or df.empty:
            continue

        stocks += list(zip(df["代码"], df["名称"]))
        time.sleep(0.3)

    except:
        continue

stocks = list(set(stocks))
df_stock = pd.DataFrame(stocks, columns=["code","name"])

df_stock = df_stock[df_stock["code"].apply(is_main)]
df_stock = df_stock[~df_stock["name"].apply(is_bad)]

print("股票数量:", len(df_stock))

# ===== 选股 =====
results = []

for _, row in df_stock.iterrows():
    code = row["code"]
    name = row["name"]

    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

        if df is None or df.empty or len(df) < 60:
            continue

        df["ma"] = df["收盘"].rolling(MA).mean()

        if df["ma"].isna().all():
            continue

        today = df.iloc[-1]
        y1 = df.iloc[-2]
        y2 = df.iloc[-3]

        # ===== 条件 =====
        cond1 = (today["收盘"] > today["ma"] and y1["收盘"] > y1["ma"])  # 连续2天站上
        cond2 = (y1["收盘"] <= y1["ma"] and today["收盘"] > today["ma"])  # 回踩
        cond3 = today["成交量"] > y1["成交量"] * 1.25  # 放量1.25倍

        if (cond1 or cond2) and cond3:

            strength = (today["收盘"] - today["ma"]) / today["ma"]
            vol = today["成交量"] / y1["成交量"]
            momentum = (today["收盘"] - df.iloc[-5]["收盘"]) / df.iloc[-5]["收盘"]

            score = strength*50 + vol*30 + momentum*20

            results.append((code, name, df, score))

        time.sleep(0.15)

    except Exception as e:
        print("错误:", e)
        continue

print("结果数量:", len(results))

# ===== 排序 =====
results.sort(key=lambda x: x[3], reverse=True)

# ===== 画图 =====
def plot(df, code, name):
    df = df.tail(60)

    plt.figure(figsize=(10,5))
    plt.plot(df["收盘"], label="Close")
    plt.plot(df["ma"], label=f"MA{MA}")
    plt.title(f"{name} {code}")
    plt.legend()

    path = f"/tmp/{code}.png"
    plt.savefig(path)
    plt.close()

    return path

# ===== 输出 =====
today_str = datetime.now().strftime("%Y-%m-%d")

if len(results) == 0:
    send_msg(f"😴 今天没有合适的股票 | {mode} | {today_str}")
else:
    send_msg(f"🔥 今日信号 Top{min(10,len(results))} | {mode} | {today_str}")

    for i, (code, name, df, score) in enumerate(results[:10], 1):
        img = plot(df, code, name)
        send_img(img, f"{i}. {name}({code})\nScore:{round(score,2)}")
