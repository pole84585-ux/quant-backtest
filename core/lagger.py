def is_lagger(df, sector_flag):

    try:

        momentum = df["close"].pct_change().tail(5).sum()

        return 0.02 < momentum < 0.15 and sector_flag

    except:
        return False
