def detect_cycle(df):

    df = df.copy()
    df['stage'] = "UNKNOWN"

    # 🕳 黄金坑（下跌末期）
    df.loc[
        (df['涨跌幅'] < -5) &
        (df['成交量'] < df['成交量'].mean()),
        'stage'
    ] = "PIT"

    # 🚀 起爆点（首次放量上涨）
    df.loc[
        (df['涨跌幅'] > 3) &
        (df['成交量'] > df['成交量'].mean()),
        'stage'
    ] = "BREAKOUT"

    # 📈 主升浪（趋势加速）
    df.loc[
        (df['涨跌幅'] > 5) &
        (df['换手率'] < 25),
        'stage'
    ] = "TREND"

    # 🔥 龙头（强势核心）
    df.loc[
        (df['涨跌幅'] > 7),
        'stage'
    ] = "LEADER"

    return df
