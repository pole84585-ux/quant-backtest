def backtest(df):
    df["signal"] = df["收盘"] > df["MA20"]
    df["ret"] = df["收盘"].pct_change()
    df["strategy"] = df["signal"].shift(1) * df["ret"]

    return {
        "win_rate": (df["strategy"] > 0).mean(),
        "return": df["strategy"].sum()
    }
