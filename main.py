import akshare as ak
import pandas as pd
import requests
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
import time

# =====================
# Telegram 配置
# =====================
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")


def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def tg_img(path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": f})


# =====================
# 股票过滤（沪深主板）
# =====================
def is_main(code):
    return code.startswith(("000","001","002","600","601","603","605"))


def is_bad(name):
    return "ST" in name


# =====================
# 牛熊判断（上证指数）
# =====================
def get_market_mode():
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df["ma21"] = df["close"].rolling(21).mean()
        last = df.iloc[-1]
        return last["close"] >= last["ma21"], df
    except:
        return True, None


is_bull, index_df = get_market_mode()
MA = 21 if is_bull else 34
mode = "牛市(MA21)" if is_bull else "熊市(MA34)"


# =====================
# 热点板块（兜底版本）
# =====================
def get_hot_sectors():
    try:
        df = ak.stock_board_industry_name_em()

        if df is None or df.empty:
            raise Exception("empty")

        if "涨跌幅" in df.columns:
            return df.sort_values("涨跌幅", ascending=False).head(6)["板块名称"].tolist()

        return df["板块名称"].head(6).tolist()

    except:
        return ["半导体", "人工智能", "新能源", "证券", "消费电子"]


sectors = get_hot_sectors()


# =====================
# 获取股票池
# =====================
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


# =====================
# 选股逻辑
# =====================
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

        # ===== 条件 =====
        cond1 = (today["收盘"] > today["ma"] and y1["收盘"] > y1["ma"])
        cond2 = (y1["收盘"] <= y1["ma"] and today["收盘"] > today["ma"])
        cond3 = today["成交量"] > y1["成交量"]

        if (cond1 or cond2) and cond3:

            strength = (today["收盘"] - today["ma"]) / today["ma"]
            vol = today["成交量"] / y1["成交量"]
            momentum = (today["收盘"] - df.iloc[-5]["收盘"]) / df.iloc[-5]["收盘"]

            score = strength*50 + vol*30 + momentum*20

            results.append((code, name, df, score))

        time.sleep(0.15)

    except:
        continue


# =====================
# 排序
# =====================
results.sort(key=lambda x: x[3], reverse=True)


# =====================
# 画图
# =====================
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


# =====================
# 输出
# =====================
if len(results) == 0:
    tg_send(f"⚠️ 今日无信号 | {mode}")
else:
    tg_send(f"🔥 A股选股信号 Top10 | {mode} | {datetime.now().strftime('%Y-%m-%d')}")

    for i, (code, name, df, score) in enumerate(results[:10], 1):
        img = plot(df, code, name)
        tg_img(img, f"{i}. {name} ({code})\nScore:{round(score,2)}")
