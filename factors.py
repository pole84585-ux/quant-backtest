def add_indicators(df):
    df["MA5"] = df["收盘"].rolling(5).mean()
    df["MA10"] = df["收盘"].rolling(10).mean()
    df["MA20"] = df["收盘"].rolling(20).mean()
    df["VOL5"] = df["成交量"].rolling(5).mean()
    df["RET20"] = df["收盘"].pct_change(20)
    return df
