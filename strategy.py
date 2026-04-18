import pandas as pd

def rsi(df, n=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(n).mean()
    loss = (-delta.clip(upper=0)).rolling(n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def count_limit_up(df):
    pct = df["close"].pct_change()
    return (pct > 0.095).sum()


def calc_score(df, money=None):

    if df is None or len(df) < 120:
        return 0

    df = df.copy()

    df["ma5"] = df["close"].rolling(5).mean()
    df["ma10"] = df["close"].rolling(10).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    df["rsi"] = rsi(df)

    latest = df.iloc[-1]

    # ===== 基础过滤 =====
    if latest["amount"] < 2e8:
        return 0

    score = 0

    # ===== ① 龙头确认 =====
    if count_limit_up(df.tail(30)) >= 2:
        score += 25
    else:
        return 0

    # ===== ② 调整阶段 =====
    high_30 = df["close"].rolling(30).max().iloc[-1]
    drawdown = (high_30 - latest["close"]) / high_30

    if 0.1 <= drawdown <= 0.3:
        score += 15
    else:
        return 0

    vol_recent = df["volume"].tail(5).mean()
    vol_old = df["volume"].iloc[-20:-10].mean()

    if vol_recent < vol_old:
        score += 10

    # ===== ③ 二波启动 =====
    prev_high = df["close"].iloc[-20:-5].max()

    if latest["close"] > prev_high:
        score += 25
    else:
        return 0

    vol_ma5 = df["volume"].rolling(5).mean().iloc[-1]
    if latest["volume"] > vol_ma5 * 1.5:
        score += 10

    # ===== ④ 主力资金 =====
    try:
        if money is not None and len(money) >= 3:
            net = money["主力净流入"].astype(float).tail(3)
            if net.sum() > 0:
                score += 15
    except:
        pass

    # ===== ⑤ 强势区 =====
    if 50 <= latest["rsi"] <= 75:
        score += 10

    return score
