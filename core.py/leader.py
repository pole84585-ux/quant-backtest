def is_leader(df):

    try:

        ma5 = df["close"].rolling(5).mean().iloc[-1]
        ma20 = df["close"].rolling(20).mean().iloc[-1]

        breakout = df["close"].iloc[-1] > df["close"].rolling(20).max().iloc[-2]

        volume = df["volume"].iloc[-1] > df["volume"].rolling(10).mean().iloc[-1] * 1.5

        return ma5 > ma20 and breakout and volume

    except:
        return False


def strength(df):

    return (
        df["close"].pct_change().tail(5).sum() * 100 +
        df["volume"].iloc[-1] / df["volume"].rolling(10).mean().iloc[-1] * 20
    )
