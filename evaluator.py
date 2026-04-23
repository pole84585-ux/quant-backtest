import numpy as np

def evaluate(df, signal):

    df = df.copy()

    df["signal"] = signal
    df["ret"] = df["收盘"].pct_change()

    df["strategy"] = df["signal"].shift(1) * df["ret"]

    total_return = df["strategy"].sum()
    win_rate = (df["strategy"] > 0).mean()

    cum = df["strategy"].cumsum()
    drawdown = (cum.cummax() - cum).max()

    score = total_return * 0.5 + win_rate * 0.3 - drawdown * 0.2

    return score, total_return, win_rate, drawdown
