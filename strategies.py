def trend(df):
    return df["MA5"].iloc[-1] > df["MA20"].iloc[-1]

def breakout(df):
    return df["收盘"].iloc[-1] > df["收盘"].rolling(20).max().iloc[-2]

def pullback(df):
    return df["收盘"].iloc[-1] < df["MA10"].iloc[-1]
