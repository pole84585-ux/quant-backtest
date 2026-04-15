import akshare as ak
import numpy as np
import pandas as pd

# =========================
# 牛熊判断（指数趋势增强）
# =========================
def market_mode():
    df = ak.stock_zh_index_daily(symbol="sh000001")

    if df is None or len(df) < 30:
        return "BEAR"

    df = df.copy()
    df["ma21"] = df["close"].rolling(21).mean()

    idx = df["close"].iloc[-1]
    ma = df["ma21"].iloc[-1]

    slope = df["close"].iloc[-1] - df["close"].iloc[-5]

    if idx >= ma and slope > 0:
        return "BULL"
    return "BEAR"

# =========================
# 股票池（主板+去ST）
# =========================
def get_pool():
    df = ak.stock_zh_a_spot_em()

    if df is None or len(df) == 0:
        return pd.DataFrame()

    df = df.copy()

    df = df[~df["名称"].astype(str).str.contains("ST", na=False)]

    df = df[df["代码"].astype(str).str.startswith(("600","601","603","000","001"))]

    return df

# =========================
# K线数据
# =========================
def get_k(code):
    df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

    if df is None or len(df) < 30:
        return None

    df = df.rename(columns={
        "收盘": "close",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "成交量": "volume"
    })

    df = df.dropna()

    return df

# =========================
# 成交量强度
# =========================
def volume_strength(df):
    try:
        return df["volume"].iloc[-1] / df["volume"].rolling(10).mean().iloc[-1]
    except:
        return 1

# =========================
# 龙头识别（v2.0）
# =========================
def is_leader(df):
    try:
        trend = df["close"].iloc[-1] > df["close"].rolling(20).mean().iloc[-1]
        momentum = df["close"].iloc[-1] / df["close"].iloc[-5] - 1
        vol = volume_strength(df)

        return trend and momentum > 0.04 and vol > 1.2
    except:
        return False

# =========================
# 低吸点（回踩均线）
# =========================
def low_buy(df):
    try:
        ma20 = df["close"].rolling(20).mean().iloc[-1]

        d = df.iloc[-1]

        return d["low"] <= ma20 <= d["close"]
    except:
        return False

# =========================
# 熊市过滤
# =========================
def bear_filter(df):
    try:
        return df["close"].iloc[-1] > df["close"].rolling(10).mean().iloc[-1]
    except:
        return False

# =========================
# 评分系统（v2.0）
# =========================
def score(df):
    try:
        vol = volume_strength(df)
        momentum = df["close"].iloc[-1] / df["close"].iloc[-5] - 1
        ret = df["close"].pct_change().iloc[-1]

        return round(vol * 0.6 + momentum * 5 + ret * 10, 2)
    except:
        return 0

# =========================
# 主逻辑
# =========================
def select():
    mode = market_mode()
    pool = get_pool()

    if pool is None or len(pool) == 0:
        return mode, []

    res = []

    codes = pool["代码"].tolist()[:80]

    for code in codes:
        try:
            df = get_k(code)

            if df is None:
                continue

            if len(df) < 30:
                continue

            leader = is_leader(df)
            low = low_buy(df)
            s = score(df)

            # 熊市过滤
            if mode == "BEAR" and not bear_filter(df):
                continue

            if leader and low:
                res.append((code, mode, "🔥龙头低吸", s))

            elif leader:
                res.append((code, mode, "🚀龙头", s))

            elif low:
                res.append((code, mode, "🟡低吸", s))

        except:
            continue

    res = sorted(res, key=lambda x: x[3], reverse=True)

    return mode, res
