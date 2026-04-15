send_msg("测试消息")
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
    return str(code).startswith(("600","601","603","605","000","001","002"))

def is_bad(name):
    return "ST" in str(name)

# ===== 牛熊判断 =====
def get_market():
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df["ma21"] = df["close"].rolling(21).mean()
        last = df.iloc[-1]
        return last["close"] >= last["ma21"]
    except Exception as e:
        print("指数错误:", e)
        return True

is_bull = get_market()
MA = 21 if is_bull else 34
mode = "牛市(MA21)" if is_bull else "熊市(MA34)"

# ===== 热点板块 =====
def get_sectors():
    try:
        df = ak.stock_board_industry_name_em()

        if df is None or df.empty:
            raise Exception("empty")

        print("板块列:", df.columns)

        if "涨跌幅" in df.columns:
            return df.sort_values("涨跌幅", ascending=False).head(6)["板块名称"].tolist()

        if "板块名称" in df.columns:
            return df["板块名称"].head(6).tolist()

        return ["半导体","人工智能","新能源","证券","消费电子"]

    except Exception as e:
        print("板块错误:", e)
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

        print(f"{s}列:", df.columns)

        # ===== 自动识别列名 =====
        code_col = None
        name_col = None

        for c in df.columns:
            if "代码" in c or "code" in c.lower():
                code_col = c
            if "名称" in c or "name" in c.lower():
                name_col = c

        if code_col is None or name_col is None:
            continue

        for i in range(len(df)):
            stocks.append((str(df.iloc[i][code_col]), str(df.iloc[i][name_col])))

        time.sleep(0.3)

    except Exception as e:
        print("板块股票错误:", e)
        continue

print("stocks示例:", stocks[:5])

# ===== 构建DataFrame =====
if len(stocks) == 0:
    send_msg("⚠️ 股票池为空（数据源异常）")
    exit()

df_stock = pd.DataFrame(stocks, columns=["code","name"])

print("列名:", df_stock.columns)

df_stock = df_stock[df_stock["code"].apply(is_main)]
df_stock = df_stock[~df_stock["name"].apply(is_bad)]

print("过滤后股票数量:", len(df_stock))

# ===== 选股 =====
results = []

for _, row in df_stock.iterrows():
    code = row["code"]
    name = row["name"]

    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

        if df is None or df.empty or len(df) < 60:
            continue

        if "收盘" not in df.columns or "成交量" not in df.columns:
            continue

        df["ma"] = df["收盘"].rolling(MA).mean()

        if df["ma"].isna().all():
            continue

        today = df.iloc[-1]
        y1 = df.iloc[-2]

        cond1 = (today["收盘"] > today["ma"] and y1["收盘"] > y1["ma"])
        cond2 = (y1["收盘"] <= y1["ma"] and today["收盘"] > today["ma"])
        cond3 = today["成交量"] > y1["成交量"] * 1.25

        if (cond1 or cond2) and cond3:

            strength = (today["收盘"] - today["ma"]) / today["ma"]
            vol = today["成交量"] / y1["成交量"]
            momentum = (today["收盘"] - df.iloc[-5]["收盘"]) / df.iloc[-5]["收盘"]

            score = strength*50 + vol*30 + momentum*20

            results.append((code, name, df, score))

        time.sleep(0.1)

    except Exception as e:
        print("个股错误:", code, e)
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
