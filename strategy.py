import pandas as pd


# ===== RSI =====
def rsi(df, n=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(n).mean()
    loss = (-delta.clip(upper=0)).rolling(n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# ===== 涨停次数 =====
def limit_up(df):
    return (df["close"].pct_change() > 0.095).sum()


# ===== 龙头二波 + 板块共振 =====
def calc_score(df, industry_strength=0, money=None):

    if df is None or len(df) < 120:
        return 0

    df = df.copy()

    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    df["rsi"] = rsi(df)

    latest = df.iloc[-1]

    score = 0

    # =========================
    # ① 龙头确认（必须）
    # =========================
    if limit_up(df.tail(30)) < 2:
        return 0
    score += 25

    # =========================
    # ② 二波结构（关键）
    # =========================
    high_30 = df["close"].rolling(30).max().iloc[-1]
    drawdown = (high_30 - latest["close"]) / high_30

    if not (0.1 <= drawdown <= 0.3):
        return 0
    score += 15

    prev_high = df["close"].iloc[-20:-5].max()
    if latest["close"] > prev_high:
        score += 25
    else:
        return 0

    # =========================
    # ③ 量能爆发
    # =========================
    vol_ma5 = df["volume"].rolling(5).mean().iloc[-1]
    if latest["volume"] > vol_ma5 * 1.5:
        score += 10

    # =========================
    # ④ 资金（弱依赖）
    # =========================
    try:
        if money is not None and len(money) >= 3:
            if money["主力净流入"].astype(float).tail(3).sum() > 0:
                score += 10
    except:
        pass

    # =========================
    # ⑤ 板块共振（🔥核心升级）
    # =========================
    if industry_strength >= 0.7:
        score += 15
    elif industry_strength >= 0.5:
        score += 8

    # =========================
    # ⑥ RSI强势区
    # =========================
    if 50 <= latest["rsi"] <= 75:
        score += 10

    return score
