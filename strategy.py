import akshare as ak
import numpy as np

# ======================
# 指数（牛熊判断增强）
# ======================
def market_mode():
    df = ak.stock_zh_index_daily(symbol="sh000001")
    df["ma21"] = df["close"].rolling(21).mean()

    idx = df["close"].iloc[-1]
    ma = df["ma21"].iloc[-1]

    slope = df["close"].iloc[-1] - df["close"].iloc[-5]

    if idx > ma and slope > 0:
        return "BULL"
    else:
        return "BEAR"

# ======================
# 股票池
# ======================
def get_pool():
    df = ak.stock_zh_a_spot_em()

    df = df[~df["名称"].str.contains("ST")]
    df = df[df["代码"].str.startswith(("600","601","603","000","001"))]

    return df

# ======================
# K线
# ======================
def get_k(code):
    df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

    df = df.rename(columns={
        "收盘":"close",
        "开盘":"open",
        "最高":"high",
        "最低":"low",
        "成交量":"volume"
    })

    return df.dropna()

# ======================
# 主线强度（市场资金）
# ======================
def money_strength(df):
    return df["volume"].iloc[-1] / df["volume"].rolling(10).mean().iloc[-1]

# ======================
# 龙头识别（升级版）
# ======================
def is_leader(df):
    if len(df) < 30:
        return False

    trend = df["close"].iloc[-1] > df["close"].rolling(20).mean().iloc[-1]
    strength = (df["close"].iloc[-1] / df["close"].iloc[-5] - 1)
    vol = money_strength(df)

    return trend and strength > 0.04 and vol > 1.2

# ======================
# 低吸（优化）
# ======================
def low_buy(df):
    ma = df["close"].rolling(20).mean()

    d = df.iloc[-1]

    return d["low"] <= ma.iloc[-1] <= d["close"]

# ======================
# 熊市过滤增强
# ======================
def bear_filter(df):
    return df["close"].iloc[-1] > df["close"].rolling(10).mean().iloc[-1]

# ======================
# 评分系统（v2.0）
# ======================
def score(df):
    try:
        vol = money_strength(df)
        ret = df["close"].pct_change().iloc[-1]

        momentum = df["close"].iloc[-1] / df["close"].iloc[-5] - 1

        return round(vol * 0.6 + momentum * 5 + ret * 10, 2)
    except:
        return 0

# ======================
# 主逻辑
# ======================
def select():
    mode = market_mode()
    pool = get_pool()

    res = []

    for code in pool["代码"].tolist()[:80]:
        try:
            df = get_k(code)

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

    return mode, sorted(res, key=lambda x: x[3], reverse=True)
