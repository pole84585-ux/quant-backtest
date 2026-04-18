import pandas as pd


def rsi(df, n=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(n).mean()
    loss = (-delta.clip(upper=0)).rolling(n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def limit_up(df):
    return (df["close"].pct_change() > 0.095).sum()


def calc_score(df, industry_strength=0):

    if df is None or len(df) < 120:
        return 0

    df = df.copy()
    df["rsi"] = rsi(df)

    latest = df.iloc[-1]
    score = 0

    # ===== 龙头强度 =====
    if limit_up(df.tail(30)) < 2:
        return 0
    score += 25

    # ===== 二波结构 =====
    high_30 = df["close"].rolling(30).max().iloc[-1]
    drawdown = (high_30 - latest["close"]) / high_30

    if not (0.1 <= drawdown <= 0.3):
        return 0
    score += 20

    prev_high = df["close"].iloc[-20:-5].max()
    if latest["close"] > prev_high:
        score += 25
    else:
        return 0

    # ===== 量能 =====
    vol_ma5 = df["volume"].rolling(5).mean().iloc[-1]
    if latest["volume"] > vol_ma5 * 1.5:
        score += 10

    # ===== 板块共振 =====
    if industry_strength >= 0.7:
        score += 15
    elif industry_strength >= 0.5:
        score += 8

    # ===== RSI =====
    if 50 <= latest["rsi"] <= 75:
        score += 10

    return score
