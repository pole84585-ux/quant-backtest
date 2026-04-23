def is_leader(df):

    try:
        ma5 = df["close"].rolling(5).mean().iloc[-1]
        ma20 = df["close"].rolling(20).mean().iloc[-1]

        return ma5 > ma20

    except:
        return False
